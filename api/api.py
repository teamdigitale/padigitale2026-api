import os
from json import dumps

import jwt
import requests
from sanic import Blueprint
from sanic.response import json

MAILGUN_KEY = os.environ.get('MAILGUN_KEY', '')
JWT_KEY = os.environ.get('JWT_KEY', '')

bp = Blueprint("api", url_prefix="/api")

@bp.route('/users', methods=['PUT'])
async def confirm_user(req):
    try:
        signed_jwt = jwt.decode(req.json.get('jwt', ''), key=JWT_KEY, algorithms="HS256")
    except jwt.exceptions.InvalidTokenError as exc:
        return json({'message': f"{exc}"}, status=400)

    address = signed_jwt['address']

    res = requests.put(
        f"https://api.eu.mailgun.net/v3/lists/newsletter@prossimapa.gov.it/members/{address}",
        auth=('api', MAILGUN_KEY),
        data={'subscribed': 'yes'},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({'message': 'ok'})

@bp.route('/users', methods=['POST'])
async def post_user(req):
    address = req.json.get('address', '')
    fields = ['representative', 'ente', 'enteSelect', 'message']

    res = requests.post(
        "https://api.eu.mailgun.net/v3/lists/newsletter@prossimapa.gov.it/members",
        auth=('api', MAILGUN_KEY),
        data={'address': address,
              'vars': dumps({k: req.json.get(k, '') for k in fields}),
              'subscribed': 'no',
              'upsert': 'yes'},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    signed_jwt = jwt.encode(payload={'address': address}, key=JWT_KEY)

    res = requests.post(
        "https://api.eu.mailgun.net/v3/prossimapa.gov.it/messages",
        auth=('api', MAILGUN_KEY),
        data={'from': 'no-reply@prossimapa.gov.it',
              'to': address,
              'subject': 'TODO Blah blah conferma la registrazione',
              'template': 'confirmation-email',
              'h:X-Mailgun-Variables': dumps({'jwt': signed_jwt})},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({'message': 'ok'})
