import json
import re
import base64
import anthropic
from app.config import settings
from app.models import PaletteResponse, ImageScanResponse

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are Color Whisperer, an expert in seasonal color analysis and color theory.

When given a color, you analyze it and return a JSON object with the following structure. 
Return ONLY valid JSON, no markdown, no explanation, no backticks.

{
  "hex_normalized": "#RRGGBB",
  "season": "one of: Warm Spring, Light Spring, Bright Spring, Warm Autumn, Deep Autumn, Soft Autumn, Cool Winter, Deep Winter, Bright Winter, Cool Summer, Light Summer, Soft Summer",
  "vibe": "A 2-3 sentence personality-forward, evocative description of the season. Use sensory language, pop culture references, moods. Make it fun and human.",
  "undertone": "warm | cool | neutral",
  "palette": [
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Base"},
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Anchor"},
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Light"},
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Depth"},
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Highlight"}
  ]
}

Rules:
- hex_normalized must always be a valid 6-digit hex code starting with #
- The palette must have exactly 5 colors with roles: Base, Anchor, Light, Depth, Highlight
- All palette hex codes must be valid 6-digit hex codes
- The vibe should have personality — avoid dry, clinical descriptions
- Consider the color's undertone (warm/cool/neutral) carefully when assigning a season
"""


def analyze_color(color_input: str) -> PaletteResponse:
    """
    Sends the color to Claude for seasonal analysis and palette generation.
    Returns a PaletteResponse object.
    """
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Analyze this color and return the JSON: {color_input}",
            }
        ],
    )

    raw = message.content[0].text.strip()

    # Strip any accidental markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    data = json.loads(raw)

    return PaletteResponse(
        color_input=color_input,
        hex_normalized=data["hex_normalized"],
        season=data["season"],
        vibe=data["vibe"],
        undertone=data["undertone"],
        palette=data["palette"],
    )


IMAGE_SCAN_PROMPT = """You are Color Whisperer, an expert in seasonal color analysis and color theory.

The user has uploaded a photo of an item — clothing, fabric, an accessory, a paint chip, anything with color.

Your job:
1. Identify the PRIMARY color of the main item in the image (ignore background, lighting artifacts, shadows)
2. Describe what you see briefly
3. Run a full seasonal color analysis on that color

Return ONLY valid JSON, no markdown, no explanation, no backticks:

{
  "item_description": "A short, friendly description of what you see in the image (e.g. 'a rust-orange knit sweater', 'a dusty blue ceramic mug')",
  "dominant_color_name": "plain English name of the main color (e.g. 'rust orange', 'dusty blue')",
  "hex_normalized": "#RRGGBB",
  "season": "one of: Warm Spring, Light Spring, Bright Spring, Warm Autumn, Deep Autumn, Soft Autumn, Cool Winter, Deep Winter, Bright Winter, Cool Summer, Light Summer, Soft Summer",
  "season_match": "yes | maybe | no — does this color fit well in the detected season?",
  "verdict": "A fun, direct 1-2 sentence verdict on whether this item works for the season. Write like a knowledgeable friend, not a bot. E.g. 'This is peak Warm Autumn energy — wear it everywhere.' or 'Technically a Cool Winter shade, but the muted quality makes it a maybe for Soft Summer too.'",
  "vibe": "A 2-3 sentence personality-forward description of the season using sensory language and pop culture references.",
  "undertone": "warm | cool | neutral",
  "palette": [
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Base"},
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Anchor"},
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Light"},
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Depth"},
    {"hex": "#RRGGBB", "name": "Color Name", "role": "Highlight"}
  ]
}

Rules:
- Focus on the item, not the background or lighting
- hex_normalized must be a valid 6-digit hex code
- All palette hex codes must be valid 6-digit hex codes
- The palette must have exactly 5 colors
- Be decisive — give a real verdict, not a hedge
"""


def analyze_image(image_bytes: bytes, media_type: str) -> "ImageScanResponse":
    """
    Sends an image to Claude Vision for color identification and seasonal analysis.
    Returns an ImageScanResponse object.
    """
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1200,
        system=IMAGE_SCAN_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Analyze the main color of the item in this photo and return the JSON.",
                    },
                ],
            }
        ],
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    data = json.loads(raw)

    return ImageScanResponse(
        item_description=data["item_description"],
        dominant_color_name=data["dominant_color_name"],
        hex_normalized=data["hex_normalized"],
        season=data["season"],
        season_match=data["season_match"],
        verdict=data["verdict"],
        vibe=data["vibe"],
        undertone=data["undertone"],
        palette=data["palette"],
    )
