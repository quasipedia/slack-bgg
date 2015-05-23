import json
from boardgamegeek import BoardGameGeek
from werkzeug.wrappers import Request, Response

bgg = BoardGameGeek()


@Request.application
def application(request):
    g = bgg.game("Jaipur")
    return Response(json.dumps(g.name))


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application)
