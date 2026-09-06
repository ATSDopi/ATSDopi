"""
Generate a social links SVG card with REAL brand icons.
Icons fetched from simpleicons.org (stored in social_icons.json).
Custom platforms (guns.lol, Frost, ATS Pro, Potion) use styled text fallbacks.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, CARD_BG, BORDER, TEXT, TEXT_DIM, PURPLE, CYAN, INDIGO

BADGE_W = 56
BADGE_H = 56
GAP = 10

# Load real social icons
_ICONS_FILE = os.path.join(os.path.dirname(__file__), "social_icons.json")
with open(_ICONS_FILE, "r", encoding="utf-8") as f:
    SOCIAL_ICON_DATA = json.load(f)

# Social platform definitions: (display_name, color, url)
# For simpleicons-backed ones, the real logo path is in SOCIAL_ICON_DATA
# For custom ones, we use a styled text/initial fallback
SOCIALS = [
    ("guns.lol",       "#a333d8", "https://guns.lol/atsdopi",       "custom"),
    ("Discord",        "#5865f2", "https://discord.com/users/704717426729943070", "simpleicons"),
    ("Instagram",      "#e4405f", "https://instagram.com/0._ats_.0", "simpleicons"),
    ("Frost",          "#00b4d8", "https://www.frostapp.net/",       "custom"),
    ("ATS Pro",        "#7287fd", "https://www.atspro.fr/",          "custom"),
    ("Email",          "#ea4335", "mailto:atsprofessional67@gmail.com", "simpleicons"),
    ("Potion Gang",    "#9b59b6", "https://www.potiongang.fr/",      "custom"),
    ("Buy Me Coffee",  "#ffdd00", "https://buymeacoffee.com/ats_dopi", "simpleicons"),
]

# Custom icon fallbacks: (initials/short text, bg_color)
CUSTOM_ICONS = {
    "guns.lol":     ("G", "#a333d8"),
    "Frost":        ("F", "#00b4d8"),
    "ATS Pro":      ("A", "#7287fd"),
    "Potion Gang":  ("P", "#9b59b6"),
}


def _build_social_icon(name, color, icon_type, icon_size):
    """Build SVG for a social icon — real logo or styled fallback."""
    if icon_type == "simpleicons" and name in SOCIAL_ICON_DATA:
        data = SOCIAL_ICON_DATA[name]
        d = data["path_d"]
        viewBox = data["viewBox"]
        fill = "#ffffff" if color == "#ffdd00" else color
        # For yellow (buymeacoffee), use dark text
        if color == "#ffdd00":
            fill = "#222222"
        return (f'<svg width="{icon_size}" height="{icon_size}" viewBox="{viewBox}">'
                f'<path d="{d}" fill="{fill}"/></svg>')

    # Custom fallback: colored circle with initial
    if name in CUSTOM_ICONS:
        initial, bg = CUSTOM_ICONS[name]
        text_color = "#ffffff"
        if color == "#ffdd00":
            text_color = "#222222"
        return (f'<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24">'
                f'<circle cx="12" cy="12" r="11" fill="{bg}"/>'
                f'<text x="12" y="17" text-anchor="middle" font-size="14" '
                f'font-weight="bold" fill="{text_color}" font-family="sans-serif">{initial}</text>'
                f'</svg>')

    return (f'<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24">'
            f'<text x="12" y="16" text-anchor="middle" font-size="12" '
            f'fill="#888" font-family="sans-serif">?</text></svg>')


def _social_badge(x, y, name, color, url, icon_type):
    """Generate a single social badge with clickable link."""
    svg = f'  <a href="{url}" target="_blank" rel="noopener noreferrer">\n'
    svg += f'  <g transform="translate({x}, {y})">\n'
    svg += f'    <rect width="{BADGE_W}" height="{BADGE_H}" rx="12" fill="{CARD_BG}" stroke="{color}" stroke-width="1.5"/>\n'
    # Icon centered
    icon_size = 32
    icon_x = (BADGE_W - icon_size) // 2
    icon_y = 8
    icon_svg = _build_social_icon(name, color, icon_type, icon_size)
    svg += f'    <g transform="translate({icon_x}, {icon_y})">\n'
    svg += f'      {icon_svg}\n'
    svg += f'    </g>\n'
    # Label
    label_y = BADGE_H - 6
    display = name if len(name) <= 12 else name[:10] + ".."
    svg += f'    <text x="{BADGE_W // 2}" y="{label_y}" font-size="8" font-family="Segoe UI, sans-serif" fill="{TEXT}" text-anchor="middle">{display}</text>\n'
    svg += '  </g>\n'
    svg += '  </a>\n'
    return svg


def generate_socials(socials, output_path):
    """Generate the social links SVG."""
    per_row = len(socials)
    total_w = per_row * BADGE_W + (per_row - 1) * GAP + 20
    total_h = BADGE_H + 20

    svg = svg_header(total_w, total_h)
    svg += f'  <rect width="{total_w}" height="{total_h}" fill="none"/>\n'

    for i, (name, color, url, icon_type) in enumerate(socials):
        x = 10 + i * (BADGE_W + GAP)
        y = 10
        svg += _social_badge(x, y, name, color, url, icon_type)

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Social links ({len(socials)} platforms, real logos) → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    generate_socials(SOCIALS, os.path.join(assets, "socials.svg"))
