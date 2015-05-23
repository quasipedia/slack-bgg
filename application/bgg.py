import json
import ConfigParser

from boardgamegeek import BoardGameGeek
from werkzeug.wrappers import Request, Response


def get_secrets():
    config = ConfigParser.ConfigParser()
    config.read('secrets.ini')
    return [config.get('bgg', x) for x in ('incoming_token', 'hook_url')]


@Request.application
def application(request):
    print request.data
    bgg = BoardGameGeek()
    incoming_token, hook_url = get_secrets()
    g = bgg.game("Jaipur")
    return Response(json.dumps(g.name))


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application)
