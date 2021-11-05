import os
from json import dumps

import jwt
import requests
from sanic import Blueprint
from sanic.response import json

bp = Blueprint("api", url_prefix="/api")

@bp.route('/date', methods=['GET'])
async def get_ldate(request):
    return json({'date': 'today!', 'secret': os.environ.get('SECRET', '')})

@bp.route('/users', methods=['POST'])
async def post_user(req):
    mailgun_key = os.environ.get('MAILGUN_KEY', '')

    address = req.json.get('address', '')
    fields = ['representative', 'ente', 'enteSelect', 'message']

    res = requests.post(
        "https://api.eu.mailgun.net/v3/lists/newsletter@prossimapa.gov.it/members",
        auth=('api', mailgun_key),
        data={'address': address,
              'vars': dumps({k: req.json.get(k, '') for k in fields}),
              'subscribed': 'no',
              'upsert': 'yes'},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    signed_jwt = jwt.encode(payload={'address': address}, key=os.environ.get('JWT_KEY', ''))

    res = requests.post(
        "https://api.eu.mailgun.net/v3/prossimapa.gov.it/messages",
        auth=('api', mailgun_key),
        data={'from': 'no-reply@prossimapa.gov.it',
              'to': address,
              'subject': 'TODO Blah blah conferma la registrazione',
              'template': 'confirmation-email',
              'h:X-Mailgun-Variables': dumps({'jwt': signed_jwt})},
    )
    if res.status_code != 200:
        return json(res.json(), status=res.status_code)

    return json({'message': 'ok'})
