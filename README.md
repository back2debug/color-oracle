# 🎨 Color Whisperer API

> Send a color. Get your season, your vibe, and a palette that actually makes sense.

Color Whisperer is a REST API that takes any color input (hex, RGB, plain English or image) and returns a seasonal color analysis powered by Claude AI. Built as a project for a Support Engineer role at Readme.

---

## Table of Contents

- [Quickstart](#quickstart)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [POST /v1/palette](#post-v1palette)
  - [POST /v1/palette/scan](#post-v1palettescan)
  - [GET /v1/palette/seasons](#get-v1paletteseasons)
- [Error Reference](#error-reference)
- [Running Locally](#running-locally)
- [Deploying to Render](#deploying-to-render)

---

## Quickstart

```bash
curl -X POST https://api.colorme.dev/v1/palette \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"color": "#C4A882"}'
```

**Response:**
```json
{
  "color_input": "#C4A882",
  "hex_normalized": "#C4A882",
  "season": "Warm Autumn",
  "vibe": "Think golden hour, aged leather, and a cup of tea that's been sitting just long enough. Earthy, grounded, quietly luxurious.",
  "undertone": "warm",
  "palette": [
    { "hex": "#C4A882", "name": "Camel", "role": "Base" },
    { "hex": "#8B5E3C", "name": "Cognac", "role": "Anchor" },
    { "hex": "#D4B896", "name": "Sand Dollar", "role": "Light" },
    { "hex": "#6B4C2A", "name": "Chocolate", "role": "Depth" },
    { "hex": "#E8D5B7", "name": "Linen", "role": "Highlight" }
  ]
}
```

---

## Authentication

Every request requires an API key passed in the `X-API-Key` header.

```bash
-H "X-API-Key: your-api-key"
```

| Scenario | Status | Error Code |
|---|---|---|
| No header sent | `401 Unauthorized` | `missing_api_key` |
| Invalid key | `403 Forbidden` | `invalid_api_key` |
| Valid key | ✅ Request proceeds | — |

---

## Endpoints

### POST /v1/palette

Analyze a color and get back the season, vibe, and palette.

#### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `color` | string | ✅ | Hex code, RGB value, or plain color name |

**Accepted color formats:**

```json
{ "color": "#C4A882" }         // hex
{ "color": "rgb(196,168,130)" } // rgb
{ "color": "dusty rose" }       // plain name
{ "color": "terracotta" }       // plain name
{ "color": "navy" }             // plain name
```

#### Response Body

| Field | Type | Description |
|---|---|---|
| `color_input` | string | The original color you sent |
| `hex_normalized` | string | Your color as a hex code |
| `season` | string | One of 12 color seasons |
| `vibe` | string | A description of the season |
| `undertone` | string | `warm`, `cool`, or `neutral` |
| `palette` | array | 5 curated colors with roles |

**Palette roles:**

| Role | Description |
|---|---|
| `Base` | Your input color (or closest match) |
| `Anchor` | A darker grounding shade |
| `Light` | A lighter, airier companion |
| `Depth` | The deepest shade in the palette |
| `Highlight` | The brightest or lightest accent |

**Supported seasons:**

`Warm Spring` · `Light Spring` · `Bright Spring` · `Warm Autumn` · `Deep Autumn` · `Soft Autumn` · `Cool Winter` · `Deep Winter` · `Bright Winter` · `Cool Summer` · `Light Summer` · `Soft Summer`

---

### POST /v1/palette/scan

Upload a photo of any item and Color Whisperer will identify the dominant color, determine the season, and tell you whether it works perfect for when you're out shopping and forgot your color swatches.

**Supported formats:** JPEG, PNG, GIF  
**Max file size:** 5MB  
**Content-Type:** `multipart/form-data`

#### Request

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | ✅ | Photo of the item to analyze |

```bash
curl -X POST https://api.colorme.dev/v1/palette/scan \
  -H "X-API-Key: your-api-key" \
  -F "file=@/path/to/your/photo.jpg"
```

#### Response Body

Includes everything from `/v1/palette`, plus:

| Field | Type | Description |
|---|---|---|
| `item_description` | string | What Color Whisperer sees in the image (e.g. "a rust-orange knit sweater") |
| `dominant_color_name` | string | Plain English name of the main color detected |
| `season_match` | string | `yes`, `maybe`, or `no` — does this item fit the detected season? |
| `verdict` | string | A direct, friendly answer on whether this item works for the season |

#### Example Response

```json
{
  "item_description": "a rust-orange knit sweater",
  "dominant_color_name": "rust orange",
  "hex_normalized": "#B5451B",
  "season": "Warm Autumn",
  "season_match": "yes",
  "verdict": "This is peak Warm Autumn energy — wear it everywhere. Pair it with camel, olive, or dark brown and you're unstoppable.",
  "vibe": "Think golden hour, aged leather, and a cup of tea that's been sitting just long enough. Earthy, grounded, quietly luxurious.",
  "undertone": "warm",
  "palette": [
    { "hex": "#B5451B", "name": "Rust", "role": "Base" },
    { "hex": "#6B2D0E", "name": "Mahogany", "role": "Anchor" },
    { "hex": "#D4845A", "name": "Terracotta", "role": "Light" },
    { "hex": "#3D1A08", "name": "Dark Espresso", "role": "Depth" },
    { "hex": "#E8C4A0", "name": "Peach Linen", "role": "Highlight" }
  ]
}
```

#### Error: Unsupported Format

```json
{
  "error": "unsupported_format",
  "message": "We only accept JPEG, PNG, or GIF images. You sent: image/bmp"
}
```

#### Error: File Too Large

```json
{
  "error": "file_too_large",
  "message": "That image is 7.2MB. Please keep it under 5MB."
}
```

---

### GET /v1/palette/seasons

Returns all 12 color seasons with descriptions and signature colors.

#### Example Response

```json
{
  "seasons": [
    {
      "id": "warm-autumn",
      "name": "Warm Autumn",
      "description": "Rich, muted, and earthy. Think golden hour, aged leather, and a cup of tea gone slightly cold.",
      "signature_colors": ["#C4A882", "#8B5E3C", "#556B2F"]
    }
  ]
}
```

---

## Error Reference

All errors return a consistent shape:

```json
{
  "error": "http status code",
  "message": "A explanation of what went wrong."
}
```

| Status | Error Code | When it happens |
|---|---|---|
| `400` | `unparseable_color` | We couldn't figure out what color you sent |
| `400` | `unsupported_format` | Image format is not JPEG, PNG, or GIF |
| `401` | `invalid_api_key` | No `X-API-Key` header found |
| `413` | `file_too_large` | Image exceeds the 5MB limit |
| `500` | `internal_error` | Something broke on our end |

---

## Running Locally

**Prerequisites:** Python 3.11+, an Anthropic API key

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/color-oracle
cd color-oracle

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and VALID_API_KEYS

# 5. Run the server
uvicorn app.main:app --reload
```

The API will be live at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

**Test it:**
```bash
curl -X POST http://localhost:8000/v1/palette \
  -H "X-API-Key: dev-key-local" \
  -H "Content-Type: application/json" \
  -d '{"color": "dusty rose"}'
```

---

## Deploying to Render

1. Push your repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your repo
4. Set the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `ANTHROPIC_API_KEY`, `VALID_API_KEYS`, `ENVIRONMENT=production`
6. Deploy 🚀

---

Built with FastAPI · Powered by Claude · Made with 🎨 by Tracey Martin.
