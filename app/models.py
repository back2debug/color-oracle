from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class ColorSeason(str, Enum):
    warm_spring = "Warm Spring"
    light_spring = "Light Spring"
    bright_spring = "Bright Spring"
    warm_autumn = "Warm Autumn"
    deep_autumn = "Deep Autumn"
    soft_autumn = "Soft Autumn"
    cool_winter = "Cool Winter"
    deep_winter = "Deep Winter"
    bright_winter = "Bright Winter"
    cool_summer = "Cool Summer"
    light_summer = "Light Summer"
    soft_summer = "Soft Summer"


class Undertone(str, Enum):
    warm = "warm"
    cool = "cool"
    neutral = "neutral"


class PaletteColor(BaseModel):
    hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")
    name: str = Field(..., description="Human-readable color name")
    role: Literal["Base", "Anchor", "Light", "Depth", "Highlight"] = Field(
        ..., description="Role this color plays in the palette"
    )


class ColorRequest(BaseModel):
    color: str = Field(
        ...,
        description="The color to analyze. Accepts hex codes (#C4A882), RGB values (rgb(196, 168, 130)), or plain names (dusty rose, navy, terracotta).",
        examples=["#C4A882", "rgb(196, 168, 130)", "dusty rose"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"color": "#C4A882"},
                {"color": "dusty rose"},
                {"color": "rgb(196, 168, 130)"},
            ]
        }
    }


class PaletteResponse(BaseModel):
    color_input: str = Field(..., description="The original color you sent")
    hex_normalized: str = Field(
        ...,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Your color converted to a hex code",
    )
    season: ColorSeason = Field(..., description="Your color season")
    vibe: str = Field(
        ..., description="A human, personality-forward description of the season"
    )
    undertone: Undertone
    palette: List[PaletteColor] = Field(
        ..., description="A curated 5-color palette that works with your color"
    )


class SeasonDetail(BaseModel):
    id: str
    name: str
    description: str
    signature_colors: List[str]


class SeasonsResponse(BaseModel):
    seasons: List[SeasonDetail]


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Explanation of what went wrong")


class ImageScanResponse(BaseModel):
    item_description: str = Field(
        ..., description="A short description of what was detected in the image"
    )
    dominant_color_name: str = Field(
        ..., description="Plain English name of the dominant color found"
    )
    hex_normalized: str = Field(
        ...,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="The dominant color as a hex code",
    )
    season: ColorSeason = Field(..., description="The detected color season")
    season_match: Literal["yes", "maybe", "no"] = Field(
        ...,
        description="How well this item's color fits the detected season",
    )
    verdict: str = Field(
        ...,
        description="A direct, friendly verdict on whether this item works for the season",
    )
    vibe: str = Field(..., description="A description of the season")
    undertone: Undertone
    palette: List[PaletteColor] = Field(
        ..., description="A curated 5-color palette that works with the detected color"
    )
