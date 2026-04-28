# Cricify Stremio Addon

Cricify is a Stremio addon built with Python and FastAPI that provides access to live sports events and TV channels. It fetches encrypted stream information from the provider's API, decrypts it, and serves it seamlessly as a Stremio catalog and stream manifest.

## Features

- **Live TV Catalog**: Displays current live sporting events and channels in Stremio.
- **Stream Extraction**: Automatically fetches and parses stream links, including necessary HTTP headers for playback.
- **Dynamic Configuration**: Connects to Firebase Realtime Database to securely fetch the latest API endpoints.
- **Payload Decryption**: Implements AES CBC decryption to read encrypted API payloads.
- **DRM Awareness**: Extracts and passes ClearKey DRM info to Stremio (requires supported players).

## Prerequisites

- Python 3.8+
- `pip`

## Installation

1. Navigate to the addon directory:
   ```bash
   cd cricify-addon
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and fill in your specific configuration values:
   - `CRICIFY_API_KEY`: The encryption key used to decrypt payloads.
   - `CRICIFY_IV`: The initialization vector for decryption.
   - `FIREBASE_DB_URL`: The URL to your Firebase Realtime Database which holds the API base URL.
   
   *(Note: Without correct keys and database URL, the addon won't be able to fetch or decrypt streams.)*

## Running the Addon

You can start the addon by running the `main.py` script directly:

```bash
python main.py
```

Alternatively, use `uvicorn`:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The addon server will start at `http://localhost:8000/`.

## Installing in Stremio

1. Start the Cricify Addon server locally (or host it remotely).
2. Open Stremio and navigate to the **Addons** section.
3. Paste the manifest URL into the Addon search bar:
   ```
   http://localhost:8000/manifest.json
   ```
   *(If you are hosting it remotely, replace `localhost:8000` with your domain)*
4. Click **Install**.
5. You should now see "Cricify" under your Stremio catalogs and can start browsing live events!
