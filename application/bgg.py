import json
import ConfigParser

from boardgamegeek import BoardGameGeek
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import abort


def get_secrets():
    config = ConfigParser.ConfigParser()
    config.read('secrets.ini')
    return [config.get('bgg', x) for x in ('incoming_token', 'hook_url')]

valid_token, hook_url = get_secrets()


@Request.application
def application(request):
    if request.method != 'POST':
        abort(405)
    if request.form.get('token') != valid_token:
        abort(401)
    bgg = BoardGameGeek()
    g = bgg.game("Jaipur")
    return Response(json.dumps(g.name))


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application)
