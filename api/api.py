import os
import uuid
from datetime import datetime, timedelta, timezone
from json import dumps

import jwt
import requests
from sanic import Blueprint
from sanic.response import empty, json

MAILGUN_KEY = os.environ.get("MAILGUN_KEY", "")
JWT_KEY = os.environ.get("JWT_KEY", "")
CAPTCHA_KEY = os.environ.get("CAPTCHA_KEY", "")

bp = Blueprint("api", url_prefix="/api")


@bp.options("/users")
@bp.options("/territory/messages")
@bp.options("/messages")
@bp.options("/<path:path>")
async def preflight(_req, path=""):
    return empty()


@bp.post("/messages")
async def message(req):
    address = req.json.get("address", "")
    captcha = req.json.get("captcha", "")
    fields = ["representative", "messageSelect", "message"]

    res = requests.post(
        f"https://www.google.com/recaptcha/api/siteverify",
        data={"secret": CAPTCHA_KEY, "response": captcha},
    )
    if res.status_code != 200 or res.json().get("success") == False:
        return json(res.json(), status=res.status_code)

    res = requests.post(
        "https://api.eu.mailgun.net/v3/padigitale2026.gov.it/messages",
        auth=("api", MAILGUN_KEY),
        data={
            "from": "PA digitale 2026 <no-reply@padigitale2026.gov.it>",
            "to": "info@padigitale2026.gov.it",
            "subject": f"Messaggio dal form - PA digitale 2026 - {address}",
            "template": "forward-email",
            "h:Reply-To": address,
            "h:X-Mailgun-Variables": dumps({k: req.json.get(k, "") for k in fields}),
        },
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({"message": "ok"})


@bp.post("/territory/messages")
async def message(req):
    address = req.json.get("address", "")
    captcha = req.json.get("captcha", "")
    area = req.json.get("area", "")
    fields = ["argument", "name", "subject", "description"]
    area_mail = {
        "nord-est": os.environ.get("T_NORDEST_MAIL", ""),
        "lombardia": os.environ.get("T_LOMBARDIA_MAIL", ""),
        "nord-ovest": os.environ.get("T_NORDOVEST_MAIL", ""),
        "centro": os.environ.get("T_CENTRO_MAIL", ""),
        "sud-ovest": os.environ.get("T_SUDOVEST_MAIL", ""),
        "sud-est": os.environ.get("T_SUDEST_MAIL", ""),
    }
    to = area_mail[area]
    if not to:
      return json({'message': f'mapping mail not found for {area}'})

    res = requests.post(
        f"https://www.google.com/recaptcha/api/siteverify",
        data={"secret": CAPTCHA_KEY, "response": captcha},
    )
    if res.status_code != 200 or res.json().get("success") == False:
        return json(res.json(), status=res.status_code)

    res = requests.post(
        "https://api.eu.mailgun.net/v3/padigitale2026.gov.it/messages",
        auth=("api", MAILGUN_KEY),
        data={
            "from": "PA digitale 2026 <no-reply@padigitale2026.gov.it>",
            "to": to,
            "subject": f"Messaggio dal form - PA digitale 2026 - {address}",
            "template": "forward-territory-email",
            "h:Reply-To": address,
            "h:X-Mailgun-Variables": dumps({k: req.json.get(k, "") for k in fields}),
        },
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({"message": "ok"})


@bp.patch("/users/<address>/<unique_id>/unsubscribe")
async def unsubscribe_user(req, address, unique_id):
    res = requests.put(
        f"https://api.eu.mailgun.net/v3/lists/newsletter@padigitale2026.gov.it/members/{address}.{unique_id}",
        auth=("api", MAILGUN_KEY),
        data={"subscribed": "no"},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({"message": "ok"})


@bp.put("/users/<address>/<unique_id>/confirm")
async def confirm_user(req, address, unique_id):
    try:
        jwt.decode(req.json.get("jwt", ""), key=JWT_KEY, algorithms="HS256")
    except jwt.exceptions.InvalidTokenError as exc:
        return json({"message": f"{exc}"}, status=400)

    res = requests.put(
        f"https://api.eu.mailgun.net/v3/lists/newsletter@padigitale2026.gov.it/members/{address}.{unique_id}",
        auth=("api", MAILGUN_KEY),
        data={"subscribed": "yes"},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    res = requests.post(
        "https://api.eu.mailgun.net/v3/padigitale2026.gov.it/messages",
        auth=("api", MAILGUN_KEY),
        data={
            "from": "PA digitale 2026 <no-reply@padigitale2026.gov.it>",
            "to": address,
            "bcc": os.environ.get("REGISTRATION_BCC", ""),
            "subject": "PA digitale 2026 - Ti diamo il benvenuto",
            "template": "welcome-email",
            "h:X-Mailgun-Variables": dumps({"address": address, "uuid": unique_id}),
        },
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({"message": "ok"})


@bp.post("/users")
async def post_user(req):
    address = req.json.get("address", "")
    fields = [
        "representative",
        "ente",
        "enteType",
        "enteSelect",
        "messageSelect",
        "message",
    ]
    timestring = datetime.now(tz=timezone.utc).isoformat()

    # Make the new entry unique, so the user can send multiple messages even if
    # they are already subscribed
    unique_id = f"{uuid.uuid4()}"
    vars = {k: req.json.get(k, "") for k in fields}
    vars.update({"timestamp": timestring})

    res = requests.post(
        "https://api.eu.mailgun.net/v3/lists/newsletter@padigitale2026.gov.it/members",
        auth=("api", MAILGUN_KEY),
        data={
            "address": f"{address}.{unique_id}",
            "vars": dumps(vars),
            "subscribed": "no",
            "upsert": "no",
        },
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    signed_jwt = jwt.encode(
        {
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=7),
            "iat": datetime.now(tz=timezone.utc),
            "address": address,
            "uuid": unique_id,
        },
        JWT_KEY,
    )

    res = requests.post(
        "https://api.eu.mailgun.net/v3/padigitale2026.gov.it/messages",
        auth=("api", MAILGUN_KEY),
        data={
            "from": "PA digitale 2026 <no-reply@padigitale2026.gov.it>",
            "to": address,
            "bcc": os.environ.get("REGISTRATION_BCC", ""),
            "subject": "PA digitale 2026 - conferma la registrazione",
            "template": "confirmation-email",
            "h:X-Mailgun-Variables": dumps({"jwt": signed_jwt}),
        },
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({"message": "ok"})
