# -*- coding=utf8 -*-
"""Copy the Nerd Fonts glyphs into the generated font.

Most of the symbol fonts are drawn on a square design grid: every glyph is as
wide as the advance and the artwork always stays inside it.  For those the
designer has already decided how big each icon is next to its neighbours, so
the grid is mapped onto the cell and the artwork is left exactly as it was
drawn.  All that is normalised is how much of the grid a typical glyph uses,
which is what makes one set match another in apparent size.

The remaining sources are proportional and have no such grid.  There the
bounding box is measured and scaled into the cell, following the upstream
`font-patcher`; glyphs that must keep their size relative to each other are
measured together as a group and share one scale factor.

Nothing here is tuned by eye, so catching up with a new Nerd Fonts release only
needs its codepoints, and its scale groups for the proportional sources.
"""
from __future__ import annotations

import errno
import os
from collections.abc import Sequence
from typing import NamedTuple, NotRequired, TypedDict

import fontforge
import psMat


# How much of its cell an icon may fill.  This is the only knob that changes
# how big the icons look; everything else is measured from the fonts.  On a
# grid source it is a typical glyph that ends up this big, not every one of
# them: the ones the designer drew larger stay larger.
ICON_FILL = 0.92

# A glyph whose ink is narrower than one cell is taken by the terminal for a
# one-cell character and squeezed: kitty renders it at about 0.7 to 0.8 of its
# size, and the narrower it is the less it shrinks.  A row of letters therefore
# comes out visibly smaller than the icons beside it, and the narrowest of them
# (`I`, `1`) end up the tallest.  Families that have to read at icon size are
# given a common width past that line, in cells.
MIN_FAMILY_WIDTH = 1.06

# The sources that are drawn on a square design grid.  Checked by measuring
# each font: these are the ones whose glyphs all share an advance width and
# never draw outside it.
GRID_SOURCES = frozenset(
    {
        "original-source.otf",
        "devicons/devicons.otf",
        "font-awesome-extension.ttf",
        "Unicode_IEC_symbol_font.otf",
        "materialdesign/MaterialDesignIconsDesktop.ttf",
        "octicons/octicons.otf",
        "codicons/codicon.ttf",
    }
)


class Attr(TypedDict):
    """How a single glyph is fitted into the cell.

    align / valign
        Where the glyph sits in the cell.  An empty string leaves the glyph
        where it is.
    stretch
        `pa` preserves the aspect ratio, `xy` fills the cell in both
        directions.
    cells
        How many hankaku cells the glyph may fill.
    full
        Fill the whole line height instead of `ICON_FILL` of it.  This is for
        the glyphs that have to touch the cell borders, such as the Powerline
        separators.
    ypadding
        Shrink the target height by this fraction.
    overlap
        Let the glyph bleed this fraction of a cell into its neighbours, so
        that separators drawn side by side join without a seam.  A negative
        value keeps the glyph away from the borders instead.
    xy_ratio
        Upper limit for width / height, to keep a stretched glyph from
        becoming too wide.
    """

    align: str
    valign: str
    stretch: str
    cells: int
    full: bool
    ypadding: float
    overlap: float
    xy_ratio: float | None


DEFAULT_ATTR: Attr = {
    "align": "c",
    "valign": "c",
    "stretch": "pa",
    "cells": 2,
    "full": False,
    "ypadding": 0.0,
    "overlap": 0.0,
    "xy_ratio": None,
}


def _attr(**kwargs: object) -> Attr:
    return {**DEFAULT_ATTR, **kwargs}  # type: ignore[typeddict-item]


# Attributes are looked up by the codepoint in the symbol font, with "default"
# as the fallback.
Attributes = dict[int | str, Attr]

DEFAULT_ATTRIBUTES: Attributes = {"default": DEFAULT_ATTR}

# The separators have to touch the cell borders, and the ones that are drawn
# next to each other have to overlap a little so that no seam shows up.
POWERLINE_ATTRIBUTES: Attributes = {
    "default": _attr(cells=1, full=True),
    # Arrow tips
    0xE0B0: _attr(align="l", stretch="xy", cells=1, full=True, overlap=0.06, xy_ratio=0.7),
    0xE0B1: _attr(align="l", stretch="xy", cells=1, full=True, xy_ratio=0.7),
    0xE0B2: _attr(align="r", stretch="xy", cells=1, full=True, overlap=0.06, xy_ratio=0.7),
    0xE0B3: _attr(align="r", stretch="xy", cells=1, full=True, xy_ratio=0.7),
    # Inverse arrow tips
    0xE0D6: _attr(align="l", stretch="xy", cells=1, full=True, overlap=0.05, xy_ratio=0.7),
    0xE0D7: _attr(align="r", stretch="xy", cells=1, full=True, overlap=0.05, xy_ratio=0.7),
    # Rounded arcs
    0xE0B4: _attr(align="l", stretch="xy", cells=1, full=True, overlap=0.06, xy_ratio=0.59),
    0xE0B5: _attr(align="l", stretch="xy", cells=1, full=True, xy_ratio=0.5),
    0xE0B6: _attr(align="r", stretch="xy", cells=1, full=True, overlap=0.06, xy_ratio=0.59),
    0xE0B7: _attr(align="r", stretch="xy", cells=1, full=True, xy_ratio=0.5),
    # Bottom triangles
    0xE0B8: _attr(align="l", stretch="xy", cells=1, full=True, overlap=0.05),
    0xE0B9: _attr(align="l", stretch="xy", cells=1, full=True),
    0xE0BA: _attr(align="r", stretch="xy", cells=1, full=True, overlap=0.05),
    0xE0BB: _attr(align="r", stretch="xy", cells=1, full=True),
    # Top triangles
    0xE0BC: _attr(align="l", stretch="xy", cells=1, full=True, overlap=0.05),
    0xE0BD: _attr(align="l", stretch="xy", cells=1, full=True),
    0xE0BE: _attr(align="r", stretch="xy", cells=1, full=True, overlap=0.05),
    0xE0BF: _attr(align="r", stretch="xy", cells=1, full=True),
    # Flames
    0xE0C0: _attr(align="l", stretch="xy", full=True, overlap=0.05),
    0xE0C1: _attr(align="l", stretch="xy", full=True),
    0xE0C2: _attr(align="r", stretch="xy", full=True, overlap=0.05),
    0xE0C3: _attr(align="r", stretch="xy", full=True),
    # Small squares
    0xE0C4: _attr(align="l", stretch="xy", full=True, overlap=-0.03, xy_ratio=0.86),
    0xE0C5: _attr(align="r", stretch="xy", full=True, overlap=-0.03, xy_ratio=0.86),
    # Bigger squares
    0xE0C6: _attr(align="l", stretch="xy", full=True, overlap=-0.03, xy_ratio=0.78),
    0xE0C7: _attr(align="r", stretch="xy", full=True, overlap=-0.03, xy_ratio=0.78),
    # Waveform
    0xE0C8: _attr(align="l", stretch="xy", full=True, overlap=0.05),
    0xE0CA: _attr(align="r", stretch="xy", full=True, overlap=0.05),
    # Hexagons
    0xE0CC: _attr(align="l", stretch="xy", full=True, overlap=0.02, xy_ratio=0.85),
    0xE0CD: _attr(align="l", stretch="xy", full=True, xy_ratio=0.865),
    # Legos
    0xE0CE: _attr(align="l", full=True),
    0xE0CF: _attr(full=True),
    0xE0D0: _attr(align="l", full=True),
    0xE0D1: _attr(align="l", full=True),
    # Top and bottom trapezoid
    0xE0D2: _attr(align="l", stretch="xy", full=True, overlap=0.02, xy_ratio=0.7),
    0xE0D4: _attr(align="r", stretch="xy", full=True, overlap=0.02, xy_ratio=0.7),
}

# Unicode gives these one cell (East Asian Width `N` or `A`) and that is what
# the terminal reserves, so they are drawn to fit a single cell.  Nerd Fonts
# does the same: every glyph in its own fonts advances by one cell.
NARROW_ATTRIBUTES: Attributes = {"default": _attr(cells=1)}

# U+2630 is `W` instead, so the terminal reserves two cells for it.  Drawing it
# one cell wide would leave the second one to be painted over by whatever comes
# next.
TRIGRAPH_ATTRIBUTES: Attributes = {"default": _attr(overlap=-0.10)}

HEAVY_BRACKETS_ATTRIBUTES: Attributes = {
    "default": _attr(cells=1, full=True, ypadding=0.3)
}

# The bars are tiled side by side to draw a progress bar, so each of them has
# to reach the cell borders.  The circles are round and must not be stretched.
PROGRESS_BAR_ATTRIBUTES: Attributes = {
    "default": _attr(stretch="xy", cells=1, full=True, overlap=0.10),
    0xEE00: _attr(align="r", stretch="xy", cells=1, full=True, overlap=0.05),
    0xEE02: _attr(align="l", stretch="xy", cells=1, full=True, overlap=0.05),
    0xEE03: _attr(align="r", stretch="xy", cells=1, full=True, overlap=0.05),
    0xEE05: _attr(align="l", stretch="xy", cells=1, full=True, overlap=0.05),
}

PROGRESS_CIRCLE_ATTRIBUTES: Attributes = {
    "default": _attr(cells=1, full=True, overlap=-0.03)
}

# These arrows point up or down and read wrong when they are centred.
FONT_AWESOME_ATTRIBUTES: Attributes = {
    "default": DEFAULT_ATTR,
    0xF0DC: _attr(valign=""),
    0xF0DD: _attr(valign=""),
    0xF0DE: _attr(valign=""),
}


# Glyphs that only look right when they keep their size relative to each other.
# Each group is measured as a whole and every member is scaled by the group's
# factor.  Taken from the upstream `font-patcher`; the codepoints are the ones
# in the symbol font.
HEAVY_BRACKETS_GROUPS: list[Sequence[int]] = [
    range(0x276C, 0x2771 + 1),
]

# 0xEDFF is not copied over.  It only sits in the group to pad the bars
# vertically, the same way the upstream patcher uses it.
PROGRESS_BAR_GROUPS: list[Sequence[int]] = [
    range(0xEDFF, 0xEE05 + 1),
]

PROGRESS_CIRCLE_GROUPS: list[Sequence[int]] = [
    range(0xEE06, 0xEE0B + 1),
]


FONT_AWESOME_GROUPS: list[Sequence[int]] = [
    [0xF005, 0xF006, 0xF089],  # star, star empty, half star
    [*range(0xF026, 0xF028 + 1), 0xEEE8, 0xEFCF],  # volume off, down, up, x, mid
    range(0xF02B, 0xF02C + 1),  # tag, tags
    range(0xF031, 0xF035 + 1),  # font et al
    range(0xF044, 0xF046 + 1),  # edit, share, check (boxes)
    range(0xF048, 0xF052 + 1),  # multimedia buttons
    range(0xF060, 0xF063 + 1),  # arrows
    [0xF053, 0xF054, 0xF077, 0xF078],  # chevron all directions
    range(0xF07D, 0xF07E + 1),  # resize
    range(0xF0A4, 0xF0A7 + 1),  # pointing hands
    [0xF0D7, 0xF0D8, 0xF0D9, 0xF0DA, 0xF0DC, 0xF0DD, 0xF0DE],  # carets and sort
    range(0xF100, 0xF107 + 1),  # angle
    range(0xF130, 0xF131 + 1),  # mic
    range(0xF141, 0xF142 + 1),  # ellipsis
    range(0xF153, 0xF15A + 1),  # currencies
    range(0xF175, 0xF178 + 1),  # long arrows
    range(0xF182, 0xF183 + 1),  # male and female
    range(0xF221, 0xF22D + 1),  # gender or so
    range(0xF255, 0xF25B + 1),  # hand symbols
]


# The groups are searched in order, so a codepoint listed in an earlier group
# keeps that group's scale even when a later group also mentions it.
WEATHER_GROUPS: list[Sequence[int]] = [
    [0xF03C, 0xF042, 0xF045],  # degree signs
    [0xF043, 0xF044, 0xF048, 0xF04B, 0xF04C, 0xF04D, 0xF057, 0xF058, 0xF087, 0xF088],  # arrows
    range(0xF053, 0xF055 + 1),  # thermometers
    [*range(0xF059, 0xF061 + 1), 0xF0B1],  # wind directions
    range(0xF089, 0xF094 + 1),  # clocks
    range(0xF095, 0xF0B0 + 1),  # moon phases
    range(0xF0B7, 0xF0C3 + 1),  # wind strengths
    [0xF06E, 0xF070],  # solar/lunar eclipse
    [0xF051, 0xF052, 0xF0C9, 0xF0CA, 0xF072],  # sun/moon up/down
    [0xF049, 0xF056, 0xF071, *range(0xF073, 0xF07C + 1), 0xF08A],  # other things
    [
        *range(0xF000, 0xF041 + 1),
        *range(0xF064, 0xF06D + 1),
        *range(0xF07D, 0xF083 + 1),
        *range(0xF085, 0xF086 + 1),
        *range(0xF0B2, 0xF0B6 + 1),
    ],  # lots of clouds (weather states)
]


class Family(NamedTuple):
    """Glyphs that are measured against each other, not against the whole set.

    `uniform_width` gives every member the same width, condensing the wide ones
    and widening the narrow ones.  Use it where the glyphs are meant to read as
    one series; leave it off where the widths carry meaning, as with the roman
    numerals.
    """

    codes: Sequence[int]
    uniform_width: bool = False


# Material draws its letters, digits and f-keys at text size (10/24 of the
# grid) because it also ships boxed and circled variants that put them inside
# a frame.  Standing on their own they come out far smaller than every other
# icon and turn unreadable, so each family is measured against itself.
#
# Within the alphabet the designer snapped the widths to 4, 6 and 10 grid
# units: 24 of the letters were condensed to 6, but `alpha-m` and `alpha-w`
# were left at their natural 10.  Lined up in a monospaced cell those two
# tower over the rest, so the alphabet is levelled to a single width.
MATERIAL_FAMILIES: list[Family] = [
    Family(
        [
            *range(0xF0AEE, 0xF0B07 + 1),  # alpha-a .. alpha-z
            *range(0xF0B39, 0xF0B42 + 1),  # numeric-0 .. numeric-9
        ],
        uniform_width=True,
    ),
    Family(range(0xF12AB, 0xF12B3 + 1)),  # f-key f1 .. f9
    Family(range(0xF1088, 0xF1091 + 1)),  # roman numerals: widths differ by design
]


class PatchInfo(TypedDict):
    name: str
    filename: str
    sym_start: int
    sym_end: int
    src_start: int | None
    exact: bool
    attributes: NotRequired[Attributes]
    scale_groups: NotRequired[list[Sequence[int]]]
    families: NotRequired[list[Family]]


# Define the character ranges
# Symbol font ranges

PATCH_SET: list[PatchInfo] = [
    {
        "name": "Seti-UI + Custom",
        "filename": "original-source.otf",
        "sym_start": 0xE4FA,
        "sym_end": 0xE5FF,
        "src_start": 0xE5FA,
        "exact": False,
    },
    {
        "name": "Heavy Angle Brackets",
        "filename": "extraglyphs.sfd",
        "sym_start": 0x276C,
        "sym_end": 0x2771,
        "src_start": None,
        "exact": True,
        "attributes": HEAVY_BRACKETS_ATTRIBUTES,
        "scale_groups": HEAVY_BRACKETS_GROUPS,
    },
    #   {
    #       "name": "Box Drawing",
    #       "filename": "extraglyphs.sfd",
    #       "sym_start": 0x2500,
    #       "sym_end": 0x259F,
    #       "src_start": None,
    #       "exact": True,
    #   },
    {
        "name": "Progress Bars",
        "filename": "extraglyphs.sfd",
        "sym_start": 0xEE00,
        "sym_end": 0xEE05,
        "src_start": None,
        "exact": True,
        "attributes": PROGRESS_BAR_ATTRIBUTES,
        "scale_groups": PROGRESS_BAR_GROUPS,
    },
    {
        "name": "Progress Circles",
        "filename": "extraglyphs.sfd",
        "sym_start": 0xEE06,
        "sym_end": 0xEE0B,
        "src_start": None,
        "exact": True,
        "attributes": PROGRESS_CIRCLE_ATTRIBUTES,
        "scale_groups": PROGRESS_CIRCLE_GROUPS,
    },
    {
        "name": "Devicons",
        "filename": "devicons/devicons.otf",
        "sym_start": 0xE600,
        "sym_end": 0xE858,
        "src_start": 0xE700,
        "exact": False,
    },
    {
        "name": "Powerline Symbols",
        "filename": "powerline-symbols/PowerlineSymbols.otf",
        "sym_start": 0xE0A0,
        "sym_end": 0xE0A2,
        "src_start": None,
        "exact": True,
        "attributes": POWERLINE_ATTRIBUTES,
    },
    {
        "name": "Powerline Symbols",
        "filename": "powerline-symbols/PowerlineSymbols.otf",
        "sym_start": 0xE0B0,
        "sym_end": 0xE0B3,
        "src_start": None,
        "exact": True,
        "attributes": POWERLINE_ATTRIBUTES,
    },
    {
        "name": "Powerline Extra Symbols",
        "filename": "powerline-extra/PowerlineExtraSymbols.otf",
        "sym_start": 0xE0A3,
        "sym_end": 0xE0A3,
        "src_start": None,
        "exact": True,
        "attributes": POWERLINE_ATTRIBUTES,
    },
    {
        "name": "Powerline Extra Symbols",
        "filename": "powerline-extra/PowerlineExtraSymbols.otf",
        "sym_start": 0xE0B4,
        "sym_end": 0xE0C8,
        "src_start": None,
        "exact": True,
        "attributes": POWERLINE_ATTRIBUTES,
    },
    {
        "name": "Powerline Extra Symbols",
        "filename": "powerline-extra/PowerlineExtraSymbols.otf",
        "sym_start": 0xE0CA,
        "sym_end": 0xE0CA,
        "src_start": None,
        "exact": True,
        "attributes": POWERLINE_ATTRIBUTES,
    },
    {
        "name": "Powerline Extra Symbols",
        "filename": "powerline-extra/PowerlineExtraSymbols.otf",
        "sym_start": 0xE0CC,
        "sym_end": 0xE0D7,
        "src_start": None,
        "exact": True,
        "attributes": POWERLINE_ATTRIBUTES,
    },
    {
        "name": "Powerline Extra Symbols",
        "filename": "powerline-extra/PowerlineExtraSymbols.otf",
        "sym_start": 0x2630,
        "sym_end": 0x2630,
        "src_start": None,
        "exact": True,
        "attributes": TRIGRAPH_ATTRIBUTES,
    },
    {
        "name": "Pomicons",
        "filename": "pomicons/Pomicons.otf",
        "sym_start": 0xE000,
        "sym_end": 0xE00A,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Font Awesome",
        "filename": "font-awesome/FontAwesome.otf",
        "sym_start": 0xED00,
        "sym_end": 0xF2FF,
        "src_start": None,
        "exact": True,
        "attributes": FONT_AWESOME_ATTRIBUTES,
        "scale_groups": FONT_AWESOME_GROUPS,
    },  # Maximize
    {
        "name": "Font Awesome Extension",
        "filename": "font-awesome-extension.ttf",
        "sym_start": 0xE000,
        "sym_end": 0xE0A9,
        "src_start": 0xE200,
        "exact": False,
    },
    {
        "name": "Power Symbols",
        "filename": "Unicode_IEC_symbol_font.otf",
        # Heavy Circle (aka Power Off)
        "sym_start": 0x23FB,
        "sym_end": 0x23FE,
        "src_start": None,
        "exact": True,
        "attributes": NARROW_ATTRIBUTES,
    },
    {
        "name": "Power Symbols",
        "filename": "Unicode_IEC_symbol_font.otf",
        "sym_start": 0x2B58,
        "sym_end": 0x2B58,
        "src_start": None,
        "exact": True,
        "attributes": NARROW_ATTRIBUTES,
    },
    {
        "name": "Material",
        "filename": "materialdesign/MaterialDesignIconsDesktop.ttf",
        "sym_start": 0xF0001,
        "sym_end": 0xF1AF0,
        "src_start": None,
        "exact": True,
        "families": MATERIAL_FAMILIES,
    },
    {
        "name": "Weather Icons",
        "filename": "weather-icons/weathericons-regular-webfont.ttf",
        "sym_start": 0xF000,
        "sym_end": 0xF0EB,
        "src_start": 0xE300,
        "exact": False,
        "scale_groups": WEATHER_GROUPS,
    },
    {
        "name": "Font Logos",
        "filename": "font-logos.ttf",
        "sym_start": 0xF300,
        "sym_end": 0xF385,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Octicons",
        "filename": "octicons/octicons.otf",
        "sym_start": 0xF000,
        "sym_end": 0xF105,
        "src_start": 0xF400,
        "exact": False,
    },
    {
        "name": "Octicons",
        "filename": "octicons/octicons.otf",
        "sym_start": 0x2665,
        "sym_end": 0x2665,
        "src_start": None,
        "exact": True,
        "attributes": NARROW_ATTRIBUTES,
    },  # Heart
    {
        "name": "Octicons",
        "filename": "octicons/octicons.otf",
        "sym_start": 0x26A1,
        "sym_end": 0x26A1,
        "src_start": None,
        "exact": True,
    },  # Zap
    {
        "name": "Octicons",
        "filename": "octicons/octicons.otf",
        "sym_start": 0xF27C,
        "sym_end": 0xF306,
        "src_start": 0xF4A9,
        "exact": False,
    },  # Desktop
    {
        "name": "Codicons",
        "filename": "codicons/codicon.ttf",
        "sym_start": 0xEA60,
        "sym_end": 0xEC84,
        "src_start": None,
        "exact": True,
    },
]


class Box(NamedTuple):
    """A bounding box, with the advance width the measured glyphs share."""

    xmin: float
    ymin: float
    xmax: float
    ymax: float
    # None when the measured glyphs do not all have the same advance width, in
    # which case they cannot be aligned horizontally as one.
    advance: float | None

    @property
    def width(self) -> float:
        return self.xmax - self.xmin

    @property
    def height(self) -> float:
        return self.ymax - self.ymin

    @property
    def xcenter(self) -> float:
        return (self.xmin + self.xmax) / 2

    @property
    def ycenter(self) -> float:
        return (self.ymin + self.ymax) / 2

    def scale(self, x_ratio: float, y_ratio: float) -> Box:
        return Box(
            self.xmin * x_ratio,
            self.ymin * y_ratio,
            self.xmax * x_ratio,
            self.ymax * y_ratio,
            self.advance * x_ratio if self.advance is not None else None,
        )


class Cell(NamedTuple):
    """The hankaku cell of the generated font, in its own coordinates."""

    width: float
    ymin: float
    ymax: float

    @property
    def height(self) -> float:
        return self.ymax - self.ymin

    @property
    def ycenter(self) -> float:
        return (self.ymin + self.ymax) / 2


def _cell(font: fontforge.font) -> Cell:
    # A zenkaku glyph is exactly one em square wide, so a hankaku cell is half
    # of it.
    return Cell(font.em / 2, -font.descent, font.ascent)


def _bbox(glyphs: Sequence[fontforge.glyph]) -> Box | None:
    xmin = ymin = xmax = ymax = None
    advance: float | None = None
    for glyph in glyphs:
        x0, y0, x1, y1 = glyph.boundingBox()
        if len(glyphs) > 1 and x0 == x1 and y0 == y1:
            # Ignore empty glyphs when several of them are measured together.
            continue
        if xmin is None:
            xmin, ymin, xmax, ymax = x0, y0, x1, y1
            advance = glyph.width
        else:
            xmin, ymin = min(xmin, x0), min(ymin, y0)
            xmax, ymax = max(xmax, x1), max(ymax, y1)
            if advance != glyph.width:
                advance = None
    if xmin is None:
        return None
    return Box(xmin, ymin, xmax, ymax, advance if len(glyphs) > 1 else None)


def _scale_factors(src: Box, attr: Attr, cell: Cell) -> tuple[float, float]:
    if src.width <= 0 or src.height <= 0:
        return (1.0, 1.0)
    fill = 1.0 if attr["full"] else ICON_FILL
    overlap = attr["overlap"]
    target_width = cell.width * (attr["cells"] * fill + overlap)
    target_height = cell.height * fill * (1.0 - attr["ypadding"])
    if overlap:
        # Never let a glyph bleed vertically as much as it does horizontally.
        target_height *= 1.0 + min(0.01, overlap)
    x_ratio = target_width / src.width
    y_ratio = target_height / src.height
    if attr["stretch"] == "pa":
        x_ratio = y_ratio = min(x_ratio, y_ratio)
    xy_ratio = attr["xy_ratio"]
    if xy_ratio and src.width * x_ratio > src.height * y_ratio * xy_ratio:
        x_ratio = src.height * y_ratio * xy_ratio / src.width
    return (x_ratio, y_ratio)


class Canvas(NamedTuple):
    """The square design grid a symbol font is drawn on.

    Each glyph gets a canvas as wide as its own advance, sitting at `ycenter`.
    `fill` is how much of it a large glyph uses, and is what makes the sources
    comparable: without it a set that leaves a wide margin (Devicons) would
    come out visibly smaller than one that does not (Octicons).
    """

    ycenter: float
    fill: float


def _canvas(symfont: fontforge.font) -> Canvas:
    """Measure the design grid of a grid source."""
    ymin = ymax = None
    fills: list[float] = []
    for glyph in symfont.glyphs():
        if glyph.unicode < 0 or not glyph.width:
            continue
        x0, y0, x1, y1 = glyph.boundingBox()
        if x1 <= x0 or y1 <= y0:
            continue
        ymin = y0 if ymin is None else min(ymin, y0)
        ymax = y1 if ymax is None else max(ymax, y1)
        fills.append(max(x1 - x0, y1 - y0) / glyph.width)
    if ymin is None or ymax is None or not fills:
        return Canvas(symfont.em / 2, 1.0)
    fills.sort()
    # The ninth decile rather than the largest: a handful of sets have one or
    # two glyphs drawn right up to the edge, and letting those decide would
    # shrink everything else.
    return Canvas((ymin + ymax) / 2, fills[int(0.9 * (len(fills) - 1))])


def _families(
    symfont: fontforge.font, info: PatchInfo, canvas: Canvas
) -> dict[int, tuple[Canvas, float]]:
    """Give each family of glyphs a canvas measured against itself."""
    out: dict[int, tuple[Canvas, float]] = {}
    for family in info.get("families", []):
        codes = [code for code in family.codes if code in symfont]
        fills: list[float] = []
        widths: list[float] = []
        for code in codes:
            glyph = symfont[code]
            x0, y0, x1, y1 = glyph.boundingBox()
            if glyph.width and x1 > x0 and y1 > y0:
                fills.append(max(x1 - x0, y1 - y0) / glyph.width)
                widths.append(x1 - x0)
        if not fills:
            continue
        # The largest member of the family fills the cell, and the rest keep
        # their size relative to it.
        own = Canvas(canvas.ycenter, max(fills))
        widths.sort()
        common = widths[len(widths) // 2] if family.uniform_width else 0.0
        for code in codes:
            out[code] = (own, common)
    return out


def _fit_canvas(
    glyph: fontforge.glyph,
    attr: Attr,
    cell: Cell,
    canvas: Canvas,
    size: float,
    family_width: float = 0.0,
) -> None:
    """Map the source's design grid onto the cell, leaving the artwork alone."""
    width = cell.width * attr["cells"]
    ratio = width * ICON_FILL / (size * canvas.fill)
    box = _bbox([glyph])
    if box is not None:
        # The few glyphs the designer drew larger than the ninth decile would
        # run into the neighbouring cell, so hold those back at the border.
        largest = max(box.width, box.height) * ratio
        limit = min(width, cell.height)
        if largest > limit:
            ratio *= limit / largest
    x_ratio = ratio
    if family_width and box is not None and box.width > 0:
        # Every member of the family gets the same width, and the family as a
        # whole is kept wider than one cell.
        x_ratio = max(family_width * ratio, cell.width * MIN_FAMILY_WIDTH) / box.width
    glyph.transform(psMat.scale(x_ratio, ratio))
    glyph.round()
    glyph.transform(
        psMat.translate(
            (width - size * x_ratio) / 2, cell.ycenter - canvas.ycenter * ratio
        )
    )
    glyph.width = round(width)


def _fit(
    glyph: fontforge.glyph,
    attr: Attr,
    cell: Cell,
    group: Box | None,
    canvas: Canvas | None = None,
    size: float = 0.0,
    family_width: float = 0.0,
) -> None:
    """Scale the pasted glyph into its cell and move it into place."""
    if canvas is not None and size:
        _fit_canvas(glyph, attr, cell, canvas, size, family_width)
        return

    src = group or _bbox([glyph])
    if src is None:
        glyph.width = round(cell.width * attr["cells"])
        return

    x_ratio, y_ratio = _scale_factors(src, attr, cell)
    if x_ratio != 1.0 or y_ratio != 1.0:
        glyph.transform(psMat.scale(x_ratio, y_ratio))
    # ttf drops the fractional part anyway, and otf gets much smaller with it.
    glyph.round()

    # Align by the group's box when there is one, so that every member of the
    # group ends up in the same place.  A group whose glyphs have different
    # advance widths says nothing about the horizontal position, though.
    own = _bbox([glyph])
    ref = src.scale(x_ratio, y_ratio) if group else own
    if group is not None and group.advance is None and own is not None:
        ref = Box(own.xmin, ref.ymin, own.xmax, ref.ymax, None)

    x_diff = 0.0
    y_diff = 0.0
    if attr["valign"] == "c":
        y_diff = cell.ycenter - ref.ycenter
    if attr["align"]:
        width = cell.width * attr["cells"]
        overlap_width = cell.width * attr["overlap"]
        if attr["align"] == "l":
            x_diff = -ref.xmin - overlap_width
        elif attr["align"] == "r":
            x_diff = width - ref.xmax + overlap_width
        else:
            x_diff = width / 2 - ref.xcenter
    if x_diff or y_diff:
        glyph.transform(psMat.translate(x_diff, y_diff))

    glyph.width = round(cell.width * attr["cells"])


def _scale_groups(
    symfont: fontforge.font, info: PatchInfo
) -> list[tuple[set[int], Box]]:
    """Measure the combined box of each scale group once, up front."""
    groups: list[tuple[set[int], Box]] = []
    for group in info.get("scale_groups", []):
        codes = [code for code in group if code in symfont]
        if not codes:
            continue
        box = _bbox([symfont[code] for code in codes])
        if box is not None:
            groups.append((set(group), box))
    return groups


def patch(in_file: str, out_dir: str) -> int:
    font = fontforge.open(in_file)
    _patch(font)
    try:
        os.makedirs(out_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    out_file = os.path.join(out_dir, in_file)
    print(f"Generated {out_file}")
    font.generate(out_file)
    return 0


def _patch(font: fontforge.font) -> None:
    # Prevent opening and closing the fontforge font. Makes things faster when
    # patching multiple ranges using the same symbol font.
    previous_symbol_filename = ""
    symfont: fontforge.font | None = None
    canvas: Canvas | None = None
    cell = _cell(font)

    for info in PATCH_SET:
        if previous_symbol_filename != info["filename"]:
            # We have a new symbol font, so close the previous one if it exists
            if symfont:
                symfont.close()
                symfont = None
            symfont = fontforge.open(f"src/glyphs/{info['filename']}")
            symfont.encoding = "UnicodeFull"
            # Match the symbol font size to the source font size
            symfont.em = font.em
            canvas = _canvas(symfont) if info["filename"] in GRID_SOURCES else None
            previous_symbol_filename = info["filename"]

        _copy_glyphs(font, symfont, info, cell, canvas)
    if symfont:
        symfont.close()


def _codepoints(
    symfont: fontforge.font, info: PatchInfo
) -> list[tuple[int, fontforge.glyph]]:
    # A glyph can be mapped to more than one codepoint (glyph.altuni). Such a
    # glyph appears only once in byGlyphs, so collect all of its codepoints
    # here to avoid dropping the alternate ones.
    selected = symfont.selection.select(
        ("ranges", "unicode"), info["sym_start"], info["sym_end"]
    )
    found: dict[int, fontforge.glyph] = {}
    for glyph in list(selected.byGlyphs):
        altuni = glyph.altuni or ()
        for code in [glyph.unicode, *(v for v, _, _ in altuni)]:
            if info["sym_start"] <= code <= info["sym_end"]:
                found.setdefault(code, glyph)
    return sorted(found.items())


def _copy_glyphs(
    font: fontforge.font,
    symfont: fontforge.font,
    info: PatchInfo,
    cell: Cell,
    canvas: Canvas | None,
) -> None:
    attributes = info.get("attributes", DEFAULT_ATTRIBUTES)
    # A grid source needs no scale groups: the design grid already says how big
    # each glyph is next to the others.
    groups = [] if canvas else _scale_groups(symfont, info)
    families = _families(symfont, info, canvas) if canvas else {}
    copied: set[str] = set()
    for i, (code, glyph) in enumerate(_codepoints(symfont, info)):
        if info["exact"]:
            src_encoding = code + (
                s - info["sym_start"] if (s := info["src_start"]) else 0
            )
        else:
            src_encoding = (info["src_start"] or info["sym_start"]) + i
        size = symfont[code].width
        symfont.selection.select(code)
        symfont.copy()
        font.selection.select(src_encoding)
        font.paste()
        # The glyph is scaled after it has been pasted, so a glyph with
        # alternate codepoints can be copied as many times as it needs to be.
        group = next((box for codes, box in groups if code in codes), None)
        attr = attributes.get(code) or attributes["default"]
        own, family_width = families.get(code, (canvas, 0.0))
        _fit(font[src_encoding], attr, cell, group, own, size, family_width)
        # Glyph names must be unique in a font.
        first = glyph.glyphname not in copied
        copied.add(glyph.glyphname)
        font[src_encoding].glyphname = (
            glyph.glyphname if first else f"uni{src_encoding:04X}"
        )
