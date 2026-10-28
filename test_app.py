
import app as app_module


def test_home_page():
    client = app_module.app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"URL Shortener" in response.data


def test_shorten_url(monkeypatch, tmp_path):
    test_database = tmp_path / "test_urls.db"
    monkeypatch.setattr(app_module, "DATABASE", test_database)

    app_module.initialize_database()
    client = app_module.app.test_client()

    response = client.post(
        "/shorten",
        data={"original_url": "https://example.com"},
    )

    assert response.status_code == 200
    assert b"Your short link" in response.data

    with app_module.get_connection() as connection:
        saved = connection.execute(
            "SELECT original_url, short_code FROM urls"
        ).fetchone()

    assert saved["original_url"] == "https://example.com"
    assert saved["short_code"]


def test_invalid_url():
    client = app_module.app.test_client()

    response = client.post(
        "/shorten",
        data={"original_url": "not-a-valid-url"},
    )

    assert response.status_code == 400


def test_health():
    client = app_module.app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert response.json["version"] == "v1"
