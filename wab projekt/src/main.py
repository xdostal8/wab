import json
from fastapi import FastAPI
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from authlib.integrations.starlette_client import OAuth


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!secret")

# OAuth settings
GOOGLE_CLIENT_ID = "476984822533-s6526ehc2lbn5a0ma6clk6bbmepg5nb6.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

# Set up OAuth
config_data = {
    'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 
    'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET
}

from starlette.config import Config
starlette_config = Config(environ=config_data)

oauth = OAuth(starlette_config)


CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)