# Kurzvortrag: Authentifizierung (JWT & OAuth2)

## 1. Was ist Authentifizierung?
- Identitätsprüfung: Wer bist du?
- Abgrenzung: Autorisierung = Was darfst du?

## 2. Wieso Authentifizierung?
- Schutz sensibler Ressourcen
- Nachvollziehbarkeit & Vertrauen
- Minimierung von Missbrauch

## 3. Was ist JWT?
- Token-Format aus Header, Payload, Signatur
- Typische Claims: `sub`, `iat`, `exp`
- Signatur schützt vor Manipulation

**Codebeispiel: JWT ausstellen (Claims)**
```python
def issue_access_token(user_id: str, settings: Settings) -> str:
  now = int(time.time())
  ttl_seconds = settings.access_token_ttl_minutes * 60
  claims = {
    "sub": user_id,
    "iat": now,
    "exp": now + ttl_seconds,
  }
  return encode_jwt(claims, settings.secret_key)
```

## 4. Vergleich: Session-Cookies vs. JWT vs. OIDC/OAuth2
- Session-Cookies
  - Vorteil: Einfache Server-Kontrolle, leicht widerrufbar
  - Nachteil: Serverzustand, Skalierung aufwendiger
- JWT
  - Vorteil: Stateless, gut für verteilte Systeme
  - Nachteil: Widerruf schwierig, Token-Größe
- OIDC (auf OAuth2)
  - Vorteil: Standardisierte Identitätsschicht mit klaren Claims
  - Nachteil: Mehr Komplexität, mehr Konfiguration

## 5. Was ist OAuth2?
- Rollen: Resource Owner, Client, Authorization Server, Resource Server
- Authorization Code Flow mit `state` gegen CSRF

**Codebeispiel: OAuth2-Login & Callback (State-Check)**
```python
@router.get("/auth/discord/login")
async def discord_login() -> RedirectResponse:
  settings = get_settings()
  state = secrets.token_urlsafe(24)
  redirect_url = build_discord_authorize_url(state, settings)
  response = RedirectResponse(url=redirect_url)
  response.set_cookie("oauth_state", state, httponly=True, samesite="lax", max_age=600)
  return response

@router.get("/auth/discord/callback", response_model=None)
async def discord_callback(request: Request) -> RedirectResponse:
  settings = get_settings()
  query_state = request.query_params.get("state")
  cookie_state = request.cookies.get("oauth_state")
  if not query_state or cookie_state != query_state:
    raise HTTPException(status_code=400, detail="Invalid OAuth state")
  # ... code exchange, identity, token ...
```

## 6. Wieso Drittanbieter-Logins?
- Weniger Passwortverwaltung für Nutzer
- Schnellere Registrierung, weniger Abbruch
- Vertrauen durch etablierte Plattformen

## 7. Projektbezug (Kurz)
- Lokal: Registrierung/Login mit BCrypt
- Drittanbieter: Discord OAuth2
- Ausgabe: JWT für geschützte Endpunkte

**Codebeispiel: Passwort-Hashing**
```python
def hash_password(password: str) -> str:
  salt = bcrypt.gensalt()
  return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
```

**Codebeispiel: JWT-Prüfung für geschützte Routen**
```python
auth_header = request.headers.get("Authorization", "")
if not auth_header.startswith("Bearer "):
  return JSONResponse({"detail": "Missing bearer token"}, status_code=401)
token = auth_header.split(" ", 1)[1].strip()
payload = decode_jwt(token, self._settings.secret_key)
request.state.user_id = payload.get("sub")
```
