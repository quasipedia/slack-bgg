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


def send_game(channel, game):
    '''Send data about a specifig game to Slack.'''


def send_list(channel, hits):
    '''Send data about a specifig game to Slack.'''
    cells = []
    for year, name, type_, id_ in hits[:MAX_LIST_LENGTH]:
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
        'channel': '#{}'.format(channel),
        'username': BOT_NAME,
        'icon_url': ICON_URL,
        'text': '{} matching items'.format(len(hits)),
        'attachments': cells}
    requests.post(HOOK_URL, data={'payload': json.dumps(payload)})


def process(channel, query):
    '''Process a valid query.'''
    # Perform a global search
    hits = BGG.search(query, 4 | 8)  # 4 | 8 == games + expansions
    # Try to match the title exactly
    if len(hits) == 1:
        send_game(channel, BGG.game(game_id=hits[0].id))
    else:
        hits = [(h.year, h.name, h.type, h.id) for h in hits]
        send_list(channel, sorted(hits, reverse=True))


@Request.application
def application(request):
    if request.method != 'POST':
        abort(405)
    if request.form.get('token') != VALID_TOKEN:
        abort(401)
    channel = request.form['channel_name']
    query = request.form.get('text')
    if not query:
        return Response(HELP_TEXT)
    process(channel, query)
    return Response()


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application)
