import json
import ConfigParser

from boardgamegeek import BoardGameGeek
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import abort


def get_secrets():
    config = ConfigParser.ConfigParser()
    config.read('secrets.ini')
    return [config.get('bgg', x) for x in ('incoming_token', 'hook_url')]

VALID_TOKEN, HOOK_URL = get_secrets()
BGG = BoardGameGeek()
HELP_TEXT = 'Help text.'


def process(query):
    '''Process a valid query.'''
    # Perform a global search
    hits = BGG.search(query, 4 | 8)  # 4 | 8 == games + expansions
    # Try to match the title exactly
    if len(hits) == 1:
        game = BGG.game(game_id=hits[0].id)
        return Response('[{}] - {}'.format(game.year, game.name))
    d = {'boardgame': 'G', 'boardgameexpansion': 'E'}
    data = [u'{} ({}) - {} - #{}'.format(d[h.type], h.year, h.name, h.id)
            for h in hits]
    return Response(u'\n'.join(sorted(data, reverse=True)))


@Request.application
def application(request):
    if request.method != 'POST':
        abort(405)
    if request.form.get('token') != VALID_TOKEN:
        abort(401)
    query = request.form.get('text')
    if not query:
        return Response(HELP_TEXT)
    return process(query)


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application)
