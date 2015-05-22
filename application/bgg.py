from boardgamegeek import BoardGameGeek


def application(env, start_response):
    bgg = BoardGameGeek()
    g = bgg.game("Jaipur")
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["Name: {} --- ID: {}".format(g.name, g.id)]
