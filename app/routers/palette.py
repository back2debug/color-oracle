import json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.auth import require_api_key
from app.models import ColorRequest, PaletteResponse, SeasonsResponse, ErrorResponse, ImageScanResponse
from app.services.color_service import analyze_color, analyze_image

router = APIRouter(tags=["Color Whisperer"])

SEASONS_DATA = [
    {
        "id": "warm-spring",
        "name": "Warm Spring",
        "description": "Fresh, clear, and warm. Think sunlit meadows, peach blossoms, and golden hour in April.",
        "signature_colors": ["#FFB347", "#FF6B6B", "#98FB98"],
    },
    {
        "id": "light-spring",
        "name": "Light Spring",
        "description": "Delicate and luminous. The color of champagne bubbles, blush peonies, and morning light.",
        "signature_colors": ["#FFD1DC", "#FFFACD", "#B0E0E6"],
    },
    {
        "id": "bright-spring",
        "name": "Bright Spring",
        "description": "Vivid and clear. High energy, like a pop art painting or a tropical fish tank.",
        "signature_colors": ["#FF4500", "#00CED1", "#FFD700"],
    },
    {
        "id": "warm-autumn",
        "name": "Warm Autumn",
        "description": "Rich, muted, and earthy. Think golden hour, aged leather, and a cup of tea gone slightly cold.",
        "signature_colors": ["#C4A882", "#8B5E3C", "#556B2F"],
    },
    {
        "id": "deep-autumn",
        "name": "Deep Autumn",
        "description": "Dramatic and saturated. Burgundy libraries, dark forests, cognac in a crystal glass.",
        "signature_colors": ["#8B0000", "#556B2F", "#8B4513"],
    },
    {
        "id": "soft-autumn",
        "name": "Soft Autumn",
        "description": "Muted and gentle. Like a vintage polaroid — slightly faded but full of feeling.",
        "signature_colors": ["#C4A882", "#9C8B75", "#8FBC8F"],
    },
    {
        "id": "cool-winter",
        "name": "Cool Winter",
        "description": "High contrast and icy. Think black turtlenecks, fresh snow, and midnight blue.",
        "signature_colors": ["#1C1C2E", "#E8E8F0", "#4169E1"],
    },
    {
        "id": "deep-winter",
        "name": "Deep Winter",
        "description": "Intense and striking. Dark, rich, and commanding — like velvet curtains and dark espresso.",
        "signature_colors": ["#000080", "#8B0000", "#2F4F4F"],
    },
    {
        "id": "bright-winter",
        "name": "Bright Winter",
        "description": "Cool and electric. Bold jewel tones, sharp contrast — the life of any party.",
        "signature_colors": ["#FF0080", "#00FFFF", "#FFFFFF"],
    },
    {
        "id": "cool-summer",
        "name": "Cool Summer",
        "description": "Soft and cool. Faded denim, lavender fields, and silver jewelry on a cloudy day.",
        "signature_colors": ["#B0C4DE", "#DDA0DD", "#F0F8FF"],
    },
    {
        "id": "light-summer",
        "name": "Light Summer",
        "description": "Airy and muted. Think watercolor paintings, sea glass, and linen in the breeze.",
        "signature_colors": ["#E6E6FA", "#B0C4DE", "#F0FFF0"],
    },
    {
        "id": "soft-summer",
        "name": "Soft Summer",
        "description": "Cool and dusty. Vintage roses, muted mauve, the inside of an old bookshop.",
        "signature_colors": ["#BC8F8F", "#778899", "#D8BFD8"],
    },
]


@router.post(
    "/palette",
    response_model=PaletteResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Could not parse the color input"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        500: {"model": ErrorResponse, "description": "Something went wrong on our end"},
    },
    summary="Analyze a color",
    description="""
Send any color — as a hex code, RGB value, or plain name like **dusty rose** — and get back:
- Your **color season** (one of 12 seasonal archetypes)
- A **description** written like a seasoned analyst, not a spec sheet
- Your color's **undertone** (warm, cool, or neutral)
- A curated **5-color palette** that flatters your color

Great for designers, stylists, or anyone who has ever stared at a paint swatch and felt nothing.
    """,
)
async def analyze(
    body: ColorRequest,
    _: str = Depends(require_api_key),
):
    try:
        result = analyze_color(body.color)
        return result
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "parse_error",
                "message": "Something went sideways parsing the color analysis. Try again.",
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "unparseable_color",
                "message": f"We couldn't figure out what color '{body.color}' is. Try a hex code, RGB value, or a plain color name like 'dusty rose'.",
            },
        )
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Something broke on our end. We're on it.",
            },
        )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail={
    #             "error": "internal_error",
    #             "message": "Something broke on our end. We're on it.",
    #         },
    #     )


@router.get(
    "/palette/seasons",
    response_model=SeasonsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid API key"},
    },
    summary="List all color seasons",
    description="Returns all 12 supported color seasons with descriptions and signature colors. Useful for building UI pickers or understanding the full seasonal color system.",
)
async def list_seasons(_: str = Depends(require_api_key)):
    return SeasonsResponse(seasons=SEASONS_DATA)


ALLOWED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_FILE_SIZE_MB = 5


@router.post(
    "/palette/scan",
    response_model=ImageScanResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image or unsupported format"},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        413: {"model": ErrorResponse, "description": "Image too large"},
        500: {"model": ErrorResponse, "description": "Something went wrong on our end"},
    },
    summary="Scan an image for color analysis",
    description="""
Upload a photo of any item — a sweater, a paint chip, a scarf, a couch cushion — and Color Whisperer will:

1. **Identify the dominant color** of the item in the image
2. **Determine the color season** it belongs to
3. **Give you a verdict** on whether it works for that season
4. **Return a full palette** of complementary colors

Perfect for when you're out shopping and forgot your color swatches.

**Supported formats:** JPEG, PNG, GIF  
**Max file size:** 5MB
    """,
)
async def scan_image(
    file: UploadFile = File(..., description="Photo of the item to analyze"),
    _: str = Depends(require_api_key),
):
    # Validate media type
    if file.content_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "unsupported_format",
                "message": f"We only accept JPEG, PNG, or GIF images. You sent: {file.content_type}",
            },
        )

    # Read and check file size
    image_bytes = await file.read()
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "file_too_large",
                "message": f"That image is {size_mb:.1f}MB. Please keep it under {MAX_FILE_SIZE_MB}MB.",
            },
        )

    try:
        result = analyze_image(image_bytes, file.content_type)
        return result
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "parse_error",
                "message": "Something went sideways parsing the color analysis. Try again.",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "Something broke on our end. We're on it.",
            },
        )
