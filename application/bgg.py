#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
import ConfigParser
from collections import defaultdict

from boardgamegeek import BoardGameGeek, BoardGameGeekAPIError
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import abort


def get_secrets():
    config = ConfigParser.ConfigParser()
    config.read('secrets.ini')
    return [config.get('bgg', x) for x in ('incoming_token', 'hook_url')]

VALID_TOKEN, HOOK_URL = get_secrets()
BGG = BoardGameGeek()
MAX_LIST_LENGTH = 15

BGG_URL = 'https://boardgamegeek.com'
BOT_NAME = 'BoardGameGeek'
ICON_URL = 'https://slack.com/img/icons/app-57.png'
HELP_TEXT = open('help.md').read()
MISSING_DATA_STR = 'N/A'


def fire_hook(payload):
    '''Fire the hook for Slack.'''
    requests.post(HOOK_URL, data={'payload': json.dumps(payload)})


def get_game_url(type_, id_):
    return '{}/{}/{}'.format(BGG_URL, type_, id_)


def build_cell(game, title, value=None, short=True):
    '''Return a cell for the game display.'''
    value = value or getattr(game, title) or MISSING_DATA_STR
    return {'title': title.replace('_', ' ').capitalize(),
            'value': value, 'short': short}


def display_game(channel, game_id):
    '''Retrieve and format a game based on its game ID.'''
    try:
        game = BGG.game(game_id=int(game_id[1:]))
    except ValueError:
        abort(400)  # Bad request
    except BoardGameGeekAPIError:
        abort(404)  # Not found
    url = get_game_url('game', game.id)
    play_mode = '{}-{} players aged {}+, {} minutes'.format(
        game.min_players, game.max_players, game.min_age, game.playing_time)
    if game.users_rated == 0:
        rating = MISSING_DATA_STR
    else:
        rating = '{:.2f} (based on {} votes)'.format(
            float(game.rating_average), game.users_rated)
    cells = [
        build_cell(game, 'name'),
        build_cell(game, 'alternative_names'),
        build_cell(game, 'designers'),
        build_cell(game, 'year'),
        build_cell(game, 'categories'),
        build_cell(game, 'play mode', value=play_mode),
        build_cell(game, 'mechanics'),
        build_cell(game, 'rating', value=rating),
        build_cell(game, 'description', short=False),
    ]
    text = '*{}*  <{}|BGG➚>'.format(game.name, url)
    if game.image:
        medium_size = 'https:{}_t.jpg'.format(game.image[:-4])
        text = '\n'.join((text, medium_size))
    payload = {
        'channel': channel,
        'username': BOT_NAME,
        'icon_url': ICON_URL,
        'text': text,
        'attachments': [
            {
                'fallback': u'<{}|External page on BGG>'.format(url),
                'color': 'good',
                'fields': cells,
            },
        ],
    }
    fire_hook(payload)


def preprocess_hits(hits):
    '''Preprocess the hits, marking conflicts and sorting the data.'''
    pages_per_id = defaultdict(int)
    for hit in hits:
        pages_per_id[hit.id] += 1
    data = []
    for hit in hits:
        occurrencies = pages_per_id[hit.id]
        if occurrencies == 1:
            data.append((hit.year, hit.name, hit.type, hit.id, False))
        if occurrencies > 1:
            data.append((hit.year, hit.name, hit.type, hit.id, True))
            pages_per_id[hit.id] = 0  # Other hits with same ID: discarded
    return sorted(data, reverse=True)


def search_games(channel, query):
    '''Send data about a specifig game to Slack.'''
    hits = BGG.search(query, 4 | 8)  # 4 | 8 == games + expansions
    data = preprocess_hits(hits)
    cells = []
    for year, name, type_, id_, is_conflict in data[:MAX_LIST_LENGTH]:
        url = get_game_url(type_, id_)
        if is_conflict:
            color = 'warning'
        else:
            color = '#330099' if type_ == 'boardgame' else '#66CCFF'
        cells.append({
            'fallback': u'{} <{}>'.format(name, url),
            'color': color,
            'fields': [
                {
                    'title': name,
                    'value': u'({}) #{} - <{}|BGG➚>'.format(
                        year, id_, url),
                    'short': False,
                }
            ]
        })
    hnum = len(hits)
    if hnum == 0:
        text = 'Sorry, no matches for your query. :('
    else:
        text = '{} matching items.'.format(hnum)
        if hnum > MAX_LIST_LENGTH:
            text = '{} Showing the first {} results.'.format(
                text, MAX_LIST_LENGTH)
    payload = {
        'channel': channel,
        'username': BOT_NAME,
        'icon_url': ICON_URL,
        'text': text,
        'attachments': cells}
    fire_hook(payload)


@Request.application
def application(request):
    if request.method != 'POST':
        abort(405)  # Method not allowed
    if request.form.get('token') != VALID_TOKEN:
        abort(401)  # Unauthorized
    user_name = request.form['user_name']
    channel_name = request.form['channel_name']
    query = request.form.get('text')
    if not query:
        return Response(HELP_TEXT)
    if query[0] == '#':
        if channel_name == 'directmessage':
            channel = '@{}'.format(user_name)
        else:
            channel = '#{}'.format(channel_name)
        display_game(channel, query)
    else:
        search_games('@{}'.format(user_name), query)
    return Response()


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application)
