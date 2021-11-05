
import os
from sanic.response import json
from sanic import Blueprint

bp = Blueprint("api", url_prefix="/api")

@bp.route('/date', methods=['GET'])
async def get_ldate(request):
    return json({'date': 'today!', 'secret': os.environ.get('SECRET', '')})

@bp.route('/users', methods=['POST'])
async def post_user(req):
    return json({'user': req.json})
