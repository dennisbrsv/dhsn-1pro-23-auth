# Pflichtenheft: Authentifizierung mit JWT und Discord OAuth

Stand: 2026-05-19

## 1. Zielsetzung
Das System implementiert eine moderne Authentifizierungslösung mit JWT. Nutzer können sich lokal registrieren oder per Discord anmelden. Nach erfolgreicher Identitätsprüfung wird ein JWT ausgestellt, das für geschützte Ressourcen verwendet wird.

## 2. Systemueberblick
- Backend: FastAPI (REST)
- Datenhaltung: SQLite (aiosqlite)
- Auth: JWT (HS256) + BCrypt für lokale Passwörter
- OAuth2: Discord Authorization Code Flow
- UI: Minimale HTML-Seite (Jinja2 Template) als Demo-Client

## 3. Muss-Funktionen (aus dem Lastenheft)

### LF10 Registrierung (lokal)
- Eingaben: E-Mail, Passwort
- Validierung: Pflichtfelder, E-Mail normalisieren
- Speicherung: Passwort gehasht (BCrypt)
- Antwort: JWT

### LF20 Nutzerprofil speichern
- Tabelle `users` mit Feldern: user_id, email, password_hash, discord_id, created_at
- Discord-ID wird eindeutig gespeichert (nullable)

### LF30 Passwort-Hashing
- Kein Klartext
- BCrypt als Standard

### LF40 JWT-Ausstellung
- Nach erfolgreichem Login/Registrierung (lokal oder Discord)
- JWT enthält `sub`, `iat`, `exp`

### LF50 Zugriffsschutz
- Gescützte Endpunkte prüfen Bearer Token
- Ungültige oder fehlende Tokens -> 401

### LF60 JWT-Signatur und Claims
- Signatur mit HS256 und `SECRET_KEY`
- Ablaufzeit konfigurierbar

### LF70 Discord OAuth2 Authorization Code Flow
- Redirect zu Discord mit `state`
- Callback nimmt `code` entgegen
- Code-Exchange gegen Access Token
- Abruf der Discord-Identität

### LF80 Auto-Registrierung bei Discord
- Existiert kein lokaler Nutzer, wird einer angelegt

## 4. Nicht-funktionale Anforderungen
- JWT nach RFC 7519
- OAuth2 `state` Parameter gegen CSRF
- Trennung Identitätsprüfung und Token-Issuing im Code
- Clean Code: kurze Funktionen, klare Schichten, minimale Seiteneffekte

## 5. Schnittstellen

### REST-Endpunkte
- `POST /auth/register`
  - Input: JSON oder Form (email, password)
  - Output: `{ access_token, token_type }`
- `POST /auth/login`
  - Input: JSON oder Form (email, password)
  - Output: `{ access_token, token_type }`
- `GET /auth/discord/login`
  - Redirect zu Discord
- `GET /auth/discord/callback`
  - Input: `code`, `state`
  - Output: Redirect nach `/` mit `token` Query
- `GET /protected`
  - Header: `Authorization: Bearer <token>`
  - Output: `{ message, user_id }`
- `GET /me`
  - Header: `Authorization: Bearer <token>`
  - Output: Userdaten

## 6. Datenmodell
Tabelle `users`:
- `user_id` (UUID, PK)
- `email` (String, Unique)
- `password_hash` (String, optional)
- `discord_id` (String, optional, Unique)
- `created_at` (Timestamp)

## 7. Konfiguration (ENV)
- `SECRET_KEY`
- `ACCESS_TOKEN_TTL_MINUTES`
- `DATABASE_URL`
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `DISCORD_REDIRECT_URI`
- optional: `DISCORD_AUTHORIZE_URL`, `DISCORD_TOKEN_URL`

## 8. Fehlerbehandlung
- 400 bei fehlenden Feldern oder ungültigem OAuth-Status
- 401 bei falschen Zugangsdaten oder Token
- 409 bei bereits registrierter E-Mail
- 502 bei Fehlern in externen OAuth-Aufrufen

## 9. Tests (Soll)
- Registrierung + Login + JWT Zugriff auf geschützte Endpunkte
- Discord Flow mit echtem OAuth (manuell, konfigurationsabhängig)

## 10. Abgrenzung
Nicht enthalten:
- E-Mail-Bestätigung
- Account-Linking (lokal <-> Discord)
- Rollen/Rechteverwaltung
