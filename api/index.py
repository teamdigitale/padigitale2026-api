from sanic import Sanic
from sanic.response import json
app = Sanic()


@app.route('/date', methods=['GET'])
async def get_ldate(request):
    return json({'date': 'today!'})

@app.route('/users', methods=['POST'])
async def post_user(req):
    return json({'user': req.json})
