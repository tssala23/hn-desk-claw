#!/usr/bin/env python3
"""Fill the HN Desk dashboard template and publish it to the OpenClaw dashboard.

Story facts (titles, links, points, comments, authors) come only from the
Hacker News API response in output/frontpage.json. The agent supplies only
short text in output/notes.json. Everything is HTML-escaped before rendering.
"""
import argparse
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import subprocess
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output'
TEMPLATE = ROOT / 'templates' / 'dashboard.html'
AGENT_ID = 'hn-desk'
SESSION = f'agent:{AGENT_ID}:hn-dashboard'
TITLE = 'HN Desk — Front Page'
MAX_STORIES = 10


def text(value, limit):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Expected non-empty text')
    if len(value) > limit:
        raise ValueError(f'Text longer than {limit} characters')
    return value.strip()


def load_stories():
    hits = json.loads((OUTPUT / 'frontpage.json').read_text()).get('hits')
    if not isinstance(hits, list) or not hits:
        raise ValueError('output/frontpage.json has no stories; fetch the front page again')
    stories = []
    for hit in hits[:MAX_STORIES]:
        story_id = str(hit['objectID'])
        if not story_id.isdigit():
            raise ValueError(f'Unexpected story id {story_id!r}')
        hn_url = f'https://news.ycombinator.com/item?id={story_id}'
        url = hit.get('url') or hn_url
        if urlparse(url).scheme not in ('http', 'https'):
            url = hn_url
        stories.append({
            'id': story_id, 'title': hit['title'], 'url': url, 'hn_url': hn_url,
            'domain': urlparse(url).hostname.removeprefix('www.') if url != hn_url else 'news.ycombinator.com',
            'points': int(hit.get('points') or 0), 'comments': int(hit.get('num_comments') or 0),
            'author': hit.get('author') or 'unknown',
        })
    return sorted(stories, key=lambda s: s['points'], reverse=True)


def load_notes(stories):
    notes = json.loads((OUTPUT / 'notes.json').read_text())
    takeaways = notes.get('takeaways') or {}
    unknown = set(takeaways) - {s['id'] for s in stories}
    if unknown:
        raise ValueError(f'notes.json has takeaways for unknown stories: {sorted(unknown)}')
    return text(notes.get('overview'), 300), {k: text(v, 140) for k, v in takeaways.items()}


def render():
    stories = load_stories()
    overview, takeaways = load_notes(stories)
    page = TEMPLATE.read_text()
    head, rest = page.split('<!--card-->')
    card, tail = rest.split('<!--/card-->')
    esc = lambda v: html.escape(str(v), quote=True)
    cards = []
    for rank, s in enumerate(stories, 1):
        values = {**s, 'rank': rank, 'takeaway': takeaways.get(s['id'], '')}
        block = card
        for key, value in values.items():
            block = block.replace('{{' + key + '}}', esc(value))
        cards.append(block)
    generated = datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC')
    page = head + ''.join(cards) + tail
    page = page.replace('{{generated}}', esc(generated)).replace('{{overview}}', esc(overview))
    (OUTPUT / 'dashboard.html').write_text(page)
    return page, len(stories)


def rpc(method, params):
    result = subprocess.run(['openclaw', 'gateway', 'call', method, '--json', '--params', json.dumps(params)],
                            capture_output=True, text=True, timeout=90)
    if result.returncode:
        raise RuntimeError(f'Gateway {method} failed; the dashboard was not fully updated.')
    return json.loads(result.stdout)


def publish():
    page, count = render()
    rpc('sessions.create', {'key': SESSION, 'agentId': AGENT_ID, 'label': TITLE})
    rpc('sessions.patch', {'key': SESSION, 'agentId': AGENT_ID, 'label': TITLE, 'boardPresentation': 'expanded'})
    rpc('board.widget.put', {'sessionKey': SESSION, 'agentId': AGENT_ID, 'name': 'hn-front-page', 'title': TITLE,
                             'content': {'kind': 'html', 'html': page}, 'placement': {'size': 'full'}})
    print(f'Published {count} stories to the "{TITLE}" dashboard.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['render', 'publish'])
    args = parser.parse_args()
    try:
        if args.command == 'render':
            print(f'Rendered {render()[1]} stories to output/dashboard.html')
        else:
            publish()
    except (OSError, KeyError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        raise SystemExit(f'Dashboard not updated: {error}') from None
