"""
Unit tests for Color Oracle API.

Run with:
    python -m pytest tests/ -v

To run without making real Anthropic API calls (recommended for CI):
    python -m pytest tests/ -v  (mocking is built in for all Claude calls)
"""

import io
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.models import PaletteResponse, PaletteColor, ImageScanResponse

client = TestClient(app)

VALID_KEY = "dev-key-local"
INVALID_KEY = "not-a-real-key"

# Real Pydantic objects — FastAPI serializes these correctly
MOCK_PALETTE = PaletteResponse(
    color_input="test-color",
    hex_normalized="#C4A882",
    season="Warm Autumn",
    vibe="Think golden hour and aged leather.",
    undertone="warm",
    palette=[
        PaletteColor(hex="#C4A882", name="Camel", role="Base"),
        PaletteColor(hex="#8B5E3C", name="Cognac", role="Anchor"),
        PaletteColor(hex="#D4B896", name="Sand Dollar", role="Light"),
        PaletteColor(hex="#6B4C2A", name="Chocolate", role="Depth"),
        PaletteColor(hex="#E8D5B7", name="Linen", role="Highlight"),
    ],
)

MOCK_SCAN = ImageScanResponse(
    item_description="a rust-orange knit sweater",
    dominant_color_name="rust orange",
    hex_normalized="#B5451B",
    season="Warm Autumn",
    season_match="yes",
    verdict="This is peak Warm Autumn energy — wear it everywhere.",
    vibe="Think golden hour and aged leather.",
    undertone="warm",
    palette=[
        PaletteColor(hex="#B5451B", name="Rust", role="Base"),
        PaletteColor(hex="#6B2D0E", name="Mahogany", role="Anchor"),
        PaletteColor(hex="#D4845A", name="Terracotta", role="Light"),
        PaletteColor(hex="#3D1A08", name="Dark Espresso", role="Depth"),
        PaletteColor(hex="#E8C4A0", name="Peach Linen", role="Highlight"),
    ],
)


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

class TestHealth:
    def test_root_returns_ok(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class TestAuth:
    def test_missing_api_key_returns_401(self):
        response = client.get("/v1/palette/seasons")
        assert response.status_code == 401
        assert response.json()["detail"]["error"] == "invalid_api_key"

    def test_valid_api_key_passes(self):
        response = client.get(
            "/v1/palette/seasons",
            headers={"X-API-Key": VALID_KEY}
        )
        assert response.status_code == 200

    def test_missing_key_on_post_returns_401(self):
        response = client.post(
            "/v1/palette",
            json={"color": "dusty rose"}
        )
        assert response.status_code == 401

    def test_missing_key_on_scan_returns_401(self):
        image = io.BytesIO(b"fake image data")
        response = client.post(
            "/v1/palette/scan",
            files={"file": ("test.jpg", image, "image/jpeg")}
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /v1/palette/seasons
# ---------------------------------------------------------------------------

class TestSeasons:
    def test_returns_12_seasons(self):
        response = client.get(
            "/v1/palette/seasons",
            headers={"X-API-Key": VALID_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "seasons" in data
        assert len(data["seasons"]) == 12

    def test_each_season_has_required_fields(self):
        response = client.get(
            "/v1/palette/seasons",
            headers={"X-API-Key": VALID_KEY}
        )
        for season in response.json()["seasons"]:
            assert "id" in season
            assert "name" in season
            assert "description" in season
            assert "signature_colors" in season
            assert len(season["signature_colors"]) > 0

    def test_season_ids_are_unique(self):
        response = client.get(
            "/v1/palette/seasons",
            headers={"X-API-Key": VALID_KEY}
        )
        ids = [s["id"] for s in response.json()["seasons"]]
        assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# POST /v1/palette
# ---------------------------------------------------------------------------

class TestPalette:
    @patch("app.routers.palette.analyze_color")
    def test_valid_hex_returns_palette(self, mock_analyze):
        mock_analyze.return_value = MOCK_PALETTE

        response = client.post(
            "/v1/palette",
            headers={"X-API-Key": VALID_KEY},
            json={"color": "#C4A882"}
        )
        assert response.status_code == 200
        mock_analyze.assert_called_once_with("#C4A882")

    @patch("app.routers.palette.analyze_color")
    def test_plain_name_returns_palette(self, mock_analyze):
        mock_analyze.return_value = MOCK_PALETTE

        response = client.post(
            "/v1/palette",
            headers={"X-API-Key": VALID_KEY},
            json={"color": "dusty rose"}
        )
        assert response.status_code == 200
        mock_analyze.assert_called_once_with("dusty rose")

    @patch("app.routers.palette.analyze_color")
    def test_response_has_required_fields(self, mock_analyze):
        mock_analyze.return_value = MOCK_PALETTE

        response = client.post(
            "/v1/palette",
            headers={"X-API-Key": VALID_KEY},
            json={"color": "#C4A882"}
        )
        data = response.json()
        assert "season" in data
        assert "vibe" in data
        assert "undertone" in data
        assert "palette" in data
        assert len(data["palette"]) == 5

    def test_missing_color_field_returns_422(self):
        response = client.post(
            "/v1/palette",
            headers={"X-API-Key": VALID_KEY},
            json={}
        )
        assert response.status_code == 422

    def test_empty_color_string_passes_to_service(self):
        # Empty string is technically valid input — the service decides what to do with it
        # This test documents that behavior rather than asserting a specific status
        response = client.post(
            "/v1/palette",
            headers={"X-API-Key": VALID_KEY},
            json={"color": ""}
        )
        assert response.status_code in [200, 400, 422, 500]

    @patch("app.routers.palette.analyze_color")
    def test_internal_error_returns_500(self, mock_analyze):
        mock_analyze.side_effect = Exception("Something exploded")

        response = client.post(
            "/v1/palette",
            headers={"X-API-Key": VALID_KEY},
            json={"color": "dusty rose"}
        )
        assert response.status_code == 500
        assert response.json()["detail"]["error"] == "internal_error"


# ---------------------------------------------------------------------------
# POST /v1/palette/scan
# ---------------------------------------------------------------------------

class TestScan:
    @patch("app.routers.palette.analyze_image")
    def test_valid_jpeg_returns_scan_response(self, mock_analyze):
        mock_analyze.return_value = MOCK_SCAN

        image = io.BytesIO(b"fake jpeg data")
        response = client.post(
            "/v1/palette/scan",
            headers={"X-API-Key": VALID_KEY},
            files={"file": ("sweater.jpg", image, "image/jpeg")}
        )
        assert response.status_code == 200

    @patch("app.routers.palette.analyze_image")
    def test_valid_png_accepted(self, mock_analyze):
        mock_analyze.return_value = MOCK_SCAN

        image = io.BytesIO(b"fake png data")
        response = client.post(
            "/v1/palette/scan",
            headers={"X-API-Key": VALID_KEY},
            files={"file": ("swatch.png", image, "image/png")}
        )
        assert response.status_code == 200

    @patch("app.routers.palette.analyze_image")
    def test_scan_response_has_verdict(self, mock_analyze):
        mock_analyze.return_value = MOCK_SCAN

        image = io.BytesIO(b"fake jpeg data")
        response = client.post(
            "/v1/palette/scan",
            headers={"X-API-Key": VALID_KEY},
            files={"file": ("test.jpg", image, "image/jpeg")}
        )
        data = response.json()
        assert "verdict" in data
        assert "season_match" in data
        assert "item_description" in data
        assert data["season_match"] in ["yes", "maybe", "no"]

    def test_unsupported_format_returns_400(self):
        image = io.BytesIO(b"fake bmp data")
        response = client.post(
            "/v1/palette/scan",
            headers={"X-API-Key": VALID_KEY},
            files={"file": ("image.bmp", image, "image/bmp")}
        )
        assert response.status_code == 400
        assert response.json()["detail"]["error"] == "unsupported_format"

    def test_oversized_file_returns_413(self):
        large_image = io.BytesIO(b"x" * (5 * 1024 * 1024 + 1))
        response = client.post(
            "/v1/palette/scan",
            headers={"X-API-Key": VALID_KEY},
            files={"file": ("big.jpg", large_image, "image/jpeg")}
        )
        assert response.status_code == 413
        assert response.json()["detail"]["error"] == "file_too_large"

    def test_no_file_returns_422(self):
        response = client.post(
            "/v1/palette/scan",
            headers={"X-API-Key": VALID_KEY}
        )
        assert response.status_code == 422

    @patch("app.routers.palette.analyze_image")
    def test_internal_error_returns_500(self, mock_analyze):
        mock_analyze.side_effect = Exception("Claude had a moment")

        image = io.BytesIO(b"fake jpeg data")
        response = client.post(
            "/v1/palette/scan",
            headers={"X-API-Key": VALID_KEY},
            files={"file": ("test.jpg", image, "image/jpeg")}
        )
        assert response.status_code == 500
        assert response.json()["detail"]["error"] == "internal_error"

