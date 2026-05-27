# Auth Demo

Ein auf FastAPI basierendes Authentifizierungs-Demo-Projekt mit asynchroner SQLite-Datenbank (aiosqlite). Es unterstützt sowohl standardmäßige Registrierung/Login-Funktionen mit Passwörtern (bcrypt) sowie JSON Web Tokens (JWT) zur Autorisierung als auch optionales Discord OAuth2-Login.

## 📋 Anforderungen

- Python 3.8+
- Optional: Discord Developer-Account (falls Discord OAuth2 genutzt werden soll)

## 🛠️ Installation

1. Projektverzeichnis öffnen (falls nicht bereits geschehen):
   ```bash
   cd dhsn-1pro-23-auth
   ```

2. (Empfohlen) Virtuelle Umgebung erstellen und aktivieren:
   ```bash
   python -m venv venv
   # Linux/macOS:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Konfiguration (Umgebungsvariablen)

Erstelle eine `.env` Datei im Hauptverzeichnis der Anwendung (wo sich auch `main.py` befindet), um die Anwendungskonfiguration anzupassen. Falls die Datei nicht vorhanden ist, greift das Projekt auf Standardwerte für lokale Entwicklung zurück.

Ein Beispiel für den Inhalt deiner `.env`-Datei:

```text
# Authentifizierungs-Sicherheit
SECRET_KEY="dein-sicheres-und-langes-geheimnis"
ACCESS_TOKEN_TTL_MINUTES=60

# Datenbank
DATABASE_URL="./auth.db"

# Discord OAuth2 (Erforderlich für Discord Login)
DISCORD_CLIENT_ID="Deine Discord Client ID"
DISCORD_CLIENT_SECRET="Dein Discord Client Secret"
DISCORD_REDIRECT_URI="http://127.0.0.1:8000/auth/discord/callback"
```

## 🚀 Starten des Servers

Starte den lokalen ASGI Server (Uvicorn):

```bash
uvicorn main:app --reload
```

## 📖 Verwendung & API Dokumentation

Sobald der Server gestartet ist, stehen dir standardmäßig folgende URLs zur Verfügung:

- **Webseite:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) - Die statische Startseite / das Frontend-Template.
- **Interaktive API-Dokumentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) - Hier kannst du alle Routen (z.B. `/auth/register`, `/auth/login`, oder geschützte Routen) direkt im Browser ausprobieren und testen.
- **Alternative Dokumentation (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### So testest du die API manuell
1. Rufe das **Swagger UI** unter `/docs` auf.
2. Registriere einen Benutzer über den `/auth/register` Endpoint.
3. Melde dich über den `/auth/login` Endpoint an, um einen JWT Token zu erhalten.
4. Klicke in Swagger UI oben rechts auf den **"Authorize"** Button und gib dort deine Zugangsdaten ein, um auf geschützte Routen zugreifen zu können.

## 🧩 Integration in ein eigenes Projekt (`inject_auth`)

Dieses Modul ist speziell dafür ausgelegt, als Drop-in-Lösung in bestehenden Projekten verwendet zu werden. Du kannst den Code (insbesondere das `src`-Verzeichnis) einfach in dein eigenes Projekt kopieren und die Authentifizierungs-Logik inklusive Datenbank und Routen in deine eigene App injizieren.

### So funktioniert's:

Nutze die Funktion `inject_auth` aus `src.api`, um deiner App die Auth-Features hinzuzufügen.

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI

# Passe den Import an, je nachdem wo du den Code abgelegt hast
from src.api import inject_auth

# Dein eigener (optionaler) Lifespan für Start/Shutdown-Events
@asynccontextmanager
async def my_project_lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("Eigene Dienste starten...")
    yield
    print("Eigene Dienste beenden...")

# 1. Erstelle deine App
app = FastAPI(title="Mein eigenes Projekt", lifespan=my_project_lifespan)

# 2. Füge eigene Routen hinzu, wie du es üblicherweise tust
@app.get("/meine-route")
def meine_route():
    return {"hello": "world"}

# 3. Injiziere das Auth-System
# Dies fügt das JWT-Middleware, die /auth/... Routen 
# und die Auth-Datenbank-Initialisierung automatisch hinzu.
inject_auth(app)
```

**Was macht `inject_auth` im Hintergrund?**
1. **Routen:** Lädt alle relevanten Endpunkte (z.B. `/auth/login`, `/auth/register`) in deine App.
2. **Middleware:** Aktiviert die `JwtAuthMiddleware`, um Requests mit Tokens überprüfen zu können.
3. **Lifespan (Datenbank):** Sorgt dafür, dass beim Start `init_db` aufgerufen wird. Falls du der FastAPI-App bereits einen eigenen `lifespan` übergeben hast (wie im Beispiel oben), werden dein Lifespan und der Auth-Lifespan nahtlos zusammengeführt (`_compose_lifespan`).

