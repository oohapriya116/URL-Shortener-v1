
import os
import secrets
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, render_template_string, request, url_for

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(
    os.environ.get("DATABASE_PATH", str(BASE_DIR / "urls.db"))
)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>URL Shortener V1</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 760px;
            margin: 60px auto;
            padding: 20px;
            background: #f3f6fb;
            color: #172033;
        }
        main {
            background: white;
            padding: 32px;
            border-radius: 14px;
            box-shadow: 0 4px 20px #00000010;
        }
        input {
            box-sizing: border-box;
            width: 100%;
            padding: 12px;
            margin: 12px 0;
        }
        button {
            padding: 12px 18px;
            background: #185adb;
            color: white;
            border: 0;
            border-radius: 6px;
            cursor: pointer;
        }
        .result {
            overflow-wrap: anywhere;
            background: #eaf5ee;
            padding: 14px;
            margin-top: 20px;
        }
        .error { color: #b42318; }
    </style>
</head>
<body>
<main>
    <h1>URL Shortener</h1>
    <p>Version 1 — Add a URL and generate a short link.</p>

    <form action="/shorten" method="post">
        <label for="original_url">Enter your original URL</label>
        <input id="original_url" name="original_url"
               type="url" placeholder="https://example.com"
               value="{{ original_url }}" required>
        <button type="submit">Shorten URL</button>
    </form>

    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}

    {% if short_url %}
        <div class="result">
            <h2>Your short link</h2>
            <a href="{{ short_url }}">{{ short_url }}</a>
            <p>The link is saved. Redirect functionality is added in V3.</p>
        </div>
    {% endif %}

    <p>Make every link shorter and easier to share.</p>
</main>
</body>
</html>
"""


def get_connection():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DATABASE))
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def valid_url(value):
    parsed = urlparse(value)
    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
        and not any(char.isspace() for char in value)
    )


@app.get("/")
def home():
    return render_template_string(
        PAGE, original_url="", short_url="", error=""
    )


@app.post("/shorten")
def shorten():
    original_url = request.form.get("original_url", "").strip()

    if not valid_url(original_url):
        return render_template_string(
            PAGE,
            original_url=original_url,
            short_url="",
            error="Enter a valid URL starting with http:// or https://."
        ), 400

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT short_code FROM urls WHERE original_url = ?",
            (original_url,)
        ).fetchone()

        if existing:
            short_code = existing["short_code"]
        else:
            short_code = secrets.token_urlsafe(6)

            while connection.execute(
                "SELECT 1 FROM urls WHERE short_code = ?",
                (short_code,)
            ).fetchone():
                short_code = secrets.token_urlsafe(6)

            connection.execute(
                "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
                (original_url, short_code)
            )

    short_url = request.host_url.rstrip("/") + "/s/" + short_code

    return render_template_string(
        PAGE,
        original_url=original_url,
        short_url=short_url,
        error=""
    )


@app.get("/health")
def health():
    return {"status": "healthy", "version": "v1"}, 200


initialize_database()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
