import json
from boardgamegeek import BoardGameGeek


def application(env, start_response):
    bgg = BoardGameGeek()
    g = bgg.game("Jaipur")
    start_response('200 OK', [('Content-Type', 'text/html')])
    payload = {
        'text': 'Name: *{}* --- ID: *{}*\nMamma mia!'.format(g.name, g.id)
    }
    return [json.dumps(payload)]
