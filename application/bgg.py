import json
import requests
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
SITE_URL = 'https://boardgamegeek.com'
BOT_NAME = 'BoardGameGeek'
ICON_URL = 'https://slack.com/img/icons/app-57.png'
HELP_TEXT = open('help.md').read()
MAX_LIST_LENGTH = 5


def fire_hook(payload):
    '''Fire the hook for Slack.'''
    requests.post(HOOK_URL, data={'payload': json.dumps(payload)})


def display_game(channel, game_id):
    '''Retrieve and format a game based on its game ID.'''
    payload = {
        'channel': '#{}'.format(channel),
        'username': BOT_NAME,
        'icon_url': ICON_URL,
        'text': 'Single game',
        # 'attachments': cells
    }
    fire_hook(payload)


def search_games(user, query):
    '''Send data about a specifig game to Slack.'''
    hits = BGG.search(query, 4 | 8)  # 4 | 8 == games + expansions
    data = [(h.year, h.name, h.type, h.id) for h in hits]
    data.sort(reverse=True)
    cells = []
    for year, name, type_, id_ in data[:MAX_LIST_LENGTH]:
        url = '{}/{}/{}'.format(SITE_URL, type_, id_)
        htype = 'Game' if type_ == 'boardgame' else 'Expansion'
        color = 'good' if type_ == 'boardgame' else 'warning'
        cells.append({
            'fallback': u'{} <{}>'.format(name, url),
            'color': color,
            'fields': [
                {
                    'title': name,
                    'value': u'{} ({}) <{}|{}>'.format(htype, year, url, id_),
                }
            ]
        })
    payload = {
        'channel': '@{}'.format(user),
        'username': BOT_NAME,
        'icon_url': ICON_URL,
        'text': '{} matching items'.format(len(hits)),
        'attachments': cells}
    fire_hook(payload)


@Request.application
def application(request):
    if request.method != 'POST':
        abort(405)
    if request.form.get('token') != VALID_TOKEN:
        abort(401)
    user_name = request.form['user_name']
    channel_name = request.form['channel_name']
    query = request.form.get('text')
    if not query:
        return Response(HELP_TEXT)
    if query[0] == '#':
        display_game(channel_name, query)
    else:
        search_games(user_name, query)
    return Response()


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application)
