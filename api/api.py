import os
from datetime import datetime, timedelta, timezone
from json import dumps

import jwt
import requests
from sanic import Blueprint
from sanic.response import empty, json

MAILGUN_KEY = os.environ.get('MAILGUN_KEY', '')
JWT_KEY = os.environ.get('JWT_KEY', '')

bp = Blueprint("api", url_prefix="/api")

@bp.options('/users')
@bp.options('/<path:path>')
async def preflight(_req, path=''):
    return empty()

@bp.put('/users/<address>/confirm')
async def confirm_user(req, address):
    try:
        jwt.decode(req.json.get('jwt', ''), key=JWT_KEY, algorithms="HS256")
    except jwt.exceptions.InvalidTokenError as exc:
        return json({'message': f"{exc}"}, status=400)

    res = requests.put(
        f"https://api.eu.mailgun.net/v3/lists/newsletter@padigitale2026.gov.it/members/{address}",
        auth=('api', MAILGUN_KEY),
        data={'subscribed': 'yes'},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({'message': 'ok'})

@bp.post('/users')
async def post_user(req):
    address = req.json.get('address', '')
    fields = ['representative', 'ente', 'enteSelect', 'message']

    res = requests.post(
        "https://api.eu.mailgun.net/v3/lists/newsletter@padigitale2026.gov.it/members",
        auth=('api', MAILGUN_KEY),
        data={'address': address,
              'vars': dumps({k: req.json.get(k, '') for k in fields}),
              'subscribed': 'no',
              'upsert': 'no'},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    signed_jwt = jwt.encode(
        {"exp": datetime.now(tz=timezone.utc) + timedelta(days=7),
         "iat": datetime.now(tz=timezone.utc),
         "address": address},
        JWT_KEY
    )

    res = requests.post(
        "https://api.eu.mailgun.net/v3/padigitale2026.gov.it/messages",
        auth=('api', MAILGUN_KEY),
        data={'from': 'no-reply@padigitale2026.gov.it',
              'to': address,
              'bcc': os.environ.get('REGISTRATION_BCC', ''),
              'subject': 'TODO Blah blah conferma la registrazione',
              'template': 'confirmation-email',
              'h:X-Mailgun-Variables': dumps({'jwt': signed_jwt})},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({'message': 'ok'})
