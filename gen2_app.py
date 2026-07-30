"""Small dependency-free WSGI application for the Gen-2 Erfolgssoftware.

This is deliberately local-first: `run_local()` binds to 127.0.0.1. A production
rollout must run behind HTTPS with an environment-provided session secret.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import html
import os
import time
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlparse

from gen2_foundation import FoundationStore


SESSION_COOKIE = 'pm_erfolg_session'


def _sign(value: str, secret: str) -> str:
    return hmac.new(secret.encode('utf-8'), value.encode('utf-8'), hashlib.sha256).hexdigest()


def _session_value(user_id: int, secret: str, lifetime_seconds: int = 60 * 60 * 8) -> str:
    payload = f'{user_id}:{int(time.time()) + lifetime_seconds}'
    encoded = base64.urlsafe_b64encode(payload.encode('utf-8')).decode('ascii').rstrip('=')
    return f'{encoded}.{_sign(encoded, secret)}'


def _session_user_id(environ: dict, secret: str) -> int | None:
    cookie = SimpleCookie(environ.get('HTTP_COOKIE', ''))
    morsel = cookie.get(SESSION_COOKIE)
    if not morsel:
        return None
    try:
        encoded, signature = morsel.value.rsplit('.', 1)
        if not hmac.compare_digest(_sign(encoded, secret), signature):
            return None
        payload = base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)).decode('utf-8')
        user_id, expires_at = payload.split(':', 1)
        return int(user_id) if int(expires_at) >= int(time.time()) else None
    except (ValueError, UnicodeDecodeError):
        return None


def _response(start_response, status: str, body: str = '', headers: list[tuple[str, str]] | None = None):
    response_headers = [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(body.encode('utf-8'))))]
    response_headers.extend(headers or [])
    start_response(status, response_headers)
    return [body.encode('utf-8')]


def _redirect(start_response, location: str, headers: list[tuple[str, str]] | None = None):
    return _response(start_response, '303 See Other', '', [('Location', location), *(headers or [])])


def _page(title: str, content: str) -> str:
    return f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>
:root{{--ink:#0B233B;--orange:#F05A28;--paper:#F7F8FA;--line:#dfe4e9;--muted:#647381}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:Arial,sans-serif}}header{{background:var(--ink);border-bottom:5px solid var(--orange);color:#fff;padding:18px 0}}.wrap{{max-width:1080px;margin:auto;padding:0 22px}}.brand{{font-size:12px;font-weight:bold;letter-spacing:.09em;text-transform:uppercase}}.brand i{{color:var(--orange);font-style:normal}}main{{padding:34px 0}}h1{{letter-spacing:-.04em;font-size:clamp(26px,4vw,40px);margin:0 0 7px}}.sub{{color:var(--muted);margin:0 0 26px;font-size:14px}}.panel{{background:#fff;border:1px solid var(--line);padding:22px;margin:16px 0}}.table{{width:100%;border-collapse:collapse}}th{{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);text-align:left;padding:0 0 12px}}td{{border-top:1px solid var(--line);padding:15px 0;font-size:14px}}td:last-child,th:last-child{{text-align:right}}.stage{{font-size:11px;font-weight:bold;text-transform:uppercase;color:var(--orange)}}a{{color:inherit}}.score{{font-weight:bold;color:var(--orange)}}.logout{{float:right;color:#fff;font-size:13px}}label{{display:block;font-size:12px;font-weight:bold;margin:13px 0 5px}}input{{width:100%;padding:12px;border:1px solid var(--line);font:inherit}}button{{border:0;background:var(--orange);color:#fff;font:inherit;font-weight:bold;padding:12px 16px;margin-top:18px;cursor:pointer}}.error{{color:#a92c19;font-size:13px}}@media(max-width:600px){{.hide-mobile{{display:none}}}}
</style></head><body>{content}</body></html>'''


def _login_page(error: str = '') -> str:
    error_html = f'<p class="error">{html.escape(error)}</p>' if error else ''
    return _page('Login · Pokale Meier Erfolgssoftware', f'''<header><div class="wrap"><div class="brand">Pokale Meier <i>·</i> Erfolgssoftware</div></div></header><main class="wrap"><section class="panel" style="max-width:470px;margin:48px auto"><h1>Willkommen zurück.</h1><p class="sub">Geschützter Zugang für Team und Kunden.</p>{error_html}<form method="post" action="/login"><label for="email">E-Mail</label><input id="email" name="email" type="email" autocomplete="username" required><label for="password">Passwort</label><input id="password" name="password" type="password" autocomplete="current-password" required><button type="submit">Sicher anmelden</button></form></section></main>''')


def _website_link(url: str) -> str:
    """Render only HTTP(S) URLs as external links; never trust stored markup."""
    clean_url = (url or '').strip()
    parsed = urlparse(clean_url)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        return html.escape(clean_url) or '—'
    safe_url = html.escape(clean_url, quote=True)
    return f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer">{safe_url}</a>'


def _dashboard(user: dict, store: FoundationStore) -> str:
    if user['role'] == 'customer':
        organisations = [store.organisation(user['organisation_id'])]
        heading = f"Deine Erfolgsakte · {organisations[0]['name']}"
        intro = 'Hier siehst du ausschließlich die freigegebenen Daten deiner Organisation.'
    else:
        organisations = store.leaderboard()
        heading = 'Erfolgssoftware'
        intro = 'Interne Übersicht: verifizierte Kundenerfolge und sichtbare Ranglistenbasis.'
    rows = ''.join(f'''<tr><td><strong>{html.escape(org['name'])}</strong><br><small>{_website_link(org.get('website_url', ''))}</small></td><td class="hide-mobile"><span class="stage">{html.escape(org['lifecycle_stage'])}</span></td><td class="score">{int(org.get('points', store.organisation_score(org['id'])['points']))} Punkte</td></tr>''' for org in organisations)
    if not rows:
        rows = '<tr><td colspan="3">Noch keine aktive Kundenorganisation.</td></tr>'
    appointments = store.visible_appointments(user['id'])
    status_labels = {
        'planned': 'Nächste Mission geplant',
        'completed': 'Termin abgeschlossen · Prüfung offen',
        'verified': 'Termin bestätigt · +1 Punkt',
    }
    appointment_rows = ''.join(f'''<tr><td><strong>{html.escape(item['title'])}</strong><br><small>{html.escape(item['scheduled_at'])}</small></td><td>{html.escape(item.get('next_steps') or 'Noch keine nächsten Schritte festgehalten.')}<br><span class="stage">{status_labels.get(item.get('status'), 'Status offen')}</span></td></tr>''' for item in appointments)
    if not appointment_rows:
        appointment_rows = '<tr><td colspan="2">Noch keine Termine vorhanden.</td></tr>'
    journey_panel = ''
    if user['role'] == 'customer':
        journey = store.organisation_journey(user['organisation_id'])
        upcoming = journey['next_appointment']
        next_step = html.escape(upcoming['next_steps']) if upcoming and upcoming.get('next_steps') else 'Dein Team legt die nächste Etappe fest.'
        journey_panel = f'''<section class="panel"><span class="stage">Verifizierter Fortschritt</span><h2>Deine nächste Auszeichnung: {html.escape(journey['next_award'])}</h2><p class="sub">Noch {journey['points_to_next_award']} Punkte bis zum nächsten sichtbaren Moment. Punkte entstehen nur nach interner Prüfung eines belegten Erfolgs.</p><p><strong>Nächster konkreter Schritt:</strong> {next_step}</p></section>'''
    return _page('Erfolgssoftware · Pokale Meier', f'''<header><div class="wrap"><a class="logout" href="/logout">Abmelden</a><div class="brand">Pokale Meier <i>·</i> Erfolgssoftware</div></div></header><main class="wrap"><h1>{html.escape(heading)}</h1><p class="sub">{html.escape(intro)}</p>{journey_panel}<section class="panel"><table class="table"><thead><tr><th>Organisation</th><th class="hide-mobile">Stufe</th><th>Punkte</th></tr></thead><tbody>{rows}</tbody></table></section><section class="panel"><h2>Termine &amp; nächste Schritte</h2><table class="table"><thead><tr><th>Termin</th><th>Nächster Schritt &amp; Status</th></tr></thead><tbody>{appointment_rows}</tbody></table></section></main>''')


def _leaderboard_page(store: FoundationStore) -> str:
    """Partner-safe leaderboard: profile and every feed item require separate approval."""
    partners = store.public_leaderboard()
    successes = store.recent_public_successes()
    top_three = ''.join(
        f'''<article class="panel"><span class="stage">Platz {rank}</span><h2>{html.escape(partner['name'])}</h2>
        <p>{html.escape(partner['public_description'] or 'Freigegebener Erfolgspartner von Pokale Meier.')}</p>
        <p><strong>{partner['points']} Leuchtfeuer-Score</strong> · {partner['success_count']} bestätigte Kundenerfolge</p>
        <p>Prozessstatus: <span class="stage">{html.escape(partner['lifecycle_stage'])}</span><br>{_website_link(partner['partner_url'] or partner['website_url'])}</p></article>'''
        for rank, partner in enumerate(partners[:3], start=1)
    ) or '<p class="sub">Noch keine Partnerprofile für die Rangliste freigegeben.</p>'
    rows = ''.join(
        f'''<tr><td>{rank:02d}</td><td><strong>{html.escape(partner['name'])}</strong><br><small>{html.escape(partner['public_description'])}</small></td><td><span class="stage">{html.escape(partner['lifecycle_stage'])}</span></td><td>{partner['success_count']}</td><td class="score">{partner['points']}</td></tr>'''
        for rank, partner in enumerate(partners, start=1)
    ) or '<tr><td colspan="5">Noch keine freigegebenen Partnerprofile.</td></tr>'
    feed = ''.join(
        f'''<tr><td><strong>{html.escape(success['title'])}</strong><br><small>{html.escape(success['organisation_name'])} · {_website_link(success['partner_url'] or success['website_url'])}</small></td><td class="score">+{success['points']}</td></tr>'''
        for success in successes
    ) or '<tr><td colspan="2">Noch keine einzeln freigegebenen Kundenerfolge.</td></tr>'
    return _page('Rangliste · Pokale Meier', f'''<header><div class="wrap"><a class="logout" href="/">Übersicht</a><div class="brand">Pokale Meier <i>·</i> Erfolgssoftware</div></div></header><main class="wrap"><h1>Rangliste · Leuchtfeuer-Score</h1><p class="sub">Nur bestätigte und für die Öffentlichkeit freigegebene Partnerprofile und Erfolge.</p><section><h2>Spitzenfeld</h2>{top_three}</section><section class="panel"><h2>Alle Erfolgspartner</h2><table class="table"><thead><tr><th>Rang</th><th>Partner</th><th>Prozess</th><th>Erfolge</th><th>Score</th></tr></thead><tbody>{rows}</tbody></table></section><section class="panel"><h2>Neue Kundenerfolge</h2><p class="sub">Dynamische Einspaltenliste · Award-Vorschau und Punkte eines bestätigten Erfolgs.</p><table class="table"><thead><tr><th>Erfolg</th><th>Punkte</th></tr></thead><tbody>{feed}</tbody></table></section></main>''')


def create_app(store: FoundationStore, session_secret: str | None = None, secure_cookies: bool = True):
    secret = session_secret or os.environ.get('PM_ERFOLGS_PORTAL_SESSION_SECRET')
    if not secret or len(secret) < 24:
        raise RuntimeError('Für die Web-App ist PM_ERFOLGS_PORTAL_SESSION_SECRET mit mindestens 24 Zeichen erforderlich.')

    def app(environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET').upper()
        if path == '/login' and method == 'GET':
            return _response(start_response, '200 OK', _login_page())
        if path == '/login' and method == 'POST':
            length = int(environ.get('CONTENT_LENGTH') or 0)
            form = parse_qs(environ['wsgi.input'].read(length).decode('utf-8'))
            user = store.authenticate(form.get('email', [''])[0], form.get('password', [''])[0])
            if not user:
                return _response(start_response, '401 Unauthorized', _login_page('E-Mail oder Passwort stimmen nicht.'))
            attributes = 'HttpOnly; SameSite=Lax; Path=/' + ('; Secure' if secure_cookies else '')
            cookie = f'{SESSION_COOKIE}={_session_value(user["id"], secret)}; {attributes}'
            return _redirect(start_response, '/', [('Set-Cookie', cookie)])
        if path == '/logout':
            return _redirect(start_response, '/login', [('Set-Cookie', f'{SESSION_COOKIE}=; Max-Age=0; HttpOnly; SameSite=Lax; Path=/')])
        if path in {'/', '/rangliste'} and method == 'GET':
            user_id = _session_user_id(environ, secret)
            if not user_id:
                return _redirect(start_response, '/login')
            try:
                user = store.user(user_id)
            except Exception:
                return _redirect(start_response, '/login')
            if not user['active']:
                return _redirect(start_response, '/login')
            page = _leaderboard_page(store) if path == '/rangliste' else _dashboard(user, store)
            return _response(start_response, '200 OK', page)
        return _response(start_response, '404 Not Found', _page('Nicht gefunden', '<main class="wrap"><h1>Nicht gefunden</h1></main>'))

    return app


def run_local(database_path: str = 'erfolgssoftware.sqlite3') -> None:
    from wsgiref.simple_server import make_server
    secret = os.environ.get('PM_ERFOLGS_PORTAL_SESSION_SECRET')
    database_path = os.environ.get('PM_ERFOLGS_PORTAL_DATABASE', database_path)
    app = create_app(FoundationStore(database_path), secret, secure_cookies=False)
    print('Lokaler Testserver: http://127.0.0.1:8765')
    make_server('127.0.0.1', 8765, app).serve_forever()


if __name__ == '__main__':
    run_local()
