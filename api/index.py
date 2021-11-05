import os

from sanic import Sanic
from sanic.response import json
app = Sanic()


@app.route('/api/date', methods=['GET'])
async def get_ldate(request):
    return json({'date': 'today!', 'secret': os.environ['SECRET']})

@app.route('/api/users', methods=['POST'])
async def post_user(req):
    return json({'user': req.json})
