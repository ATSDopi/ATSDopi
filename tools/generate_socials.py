"""
Generate individual social badge SVGs — one file per platform.
Each badge is a standalone SVG with the real brand logo.
In the README, each <img> is wrapped in an <a> link, making them clickable.
"""

import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, CARD_BG, TEXT

BADGE_W = 56
BADGE_H = 56

# Load real social icons from simpleicons
_ICONS_FILE = os.path.join(os.path.dirname(__file__), "social_icons.json")
with open(_ICONS_FILE, "r", encoding="utf-8") as f:
    SOCIAL_ICON_DATA = json.load(f)

# (display_name, color, url, icon_source, filename)
# icon_source: "simpleicons" (real logo) or "custom" (styled initial)
SOCIALS = [
    ("guns.lol",      "#a333d8", "https://guns.lol/atsdopi",                          "custom",      "social-guns.svg"),
    ("Discord",       "#5865f2", "https://discord.com/users/704717426729943070",      "simpleicons",  "social-discord.svg"),
    ("Instagram",     "#e4405f", "https://instagram.com/0._ats_.0",                    "simpleicons",  "social-instagram.svg"),
    ("Frost",         "#00b4d8", "https://www.frostapp.net/",                          "custom",      "social-frost.svg"),
    ("ATS Pro",       "#7287fd", "https://www.atspro.fr/",                             "custom",      "social-atspro.svg"),
    ("Email",         "#ea4335", "mailto:atsprofessional67@gmail.com",                 "simpleicons",  "social-email.svg"),
    ("Potion Gang",   "#9b59b6", "https://www.potiongang.fr/",                         "custom",      "social-potion.svg"),
    ("Buy Me Coffee", "#ffdd00", "https://buymeacoffee.com/ats_dopi",                  "simpleicons",  "social-buymeacoffee.svg"),
]

# Custom fallbacks: (initial, bg_color)
CUSTOM_ICONS = {
    "guns.lol":     ("G", "#a333d8"),
    "Frost":        ("F", "#00b4d8"),
    "ATS Pro":      ("A", "#7287fd"),
    "Potion Gang":  ("P", "#9b59b6"),
}


def _build_icon(name, color, icon_source, icon_size):
    """Build SVG fragment for a social icon."""
    if icon_source == "simpleicons" and name in SOCIAL_ICON_DATA:
        data = SOCIAL_ICON_DATA[name]
        d = data["path_d"]
        viewBox = data["viewBox"]
        # Use the brand color as fill — visible on dark background
        return (f'<svg width="{icon_size}" height="{icon_size}" viewBox="{viewBox}">'
                f'<path d="{d}" fill="{color}"/></svg>')

    # Custom: colored circle with initial
    if name in CUSTOM_ICONS:
        initial, bg = CUSTOM_ICONS[name]
        text_color = "#222222" if color == "#ffdd00" else "#ffffff"
        return (f'<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24">'
                f'<circle cx="12" cy="12" r="11" fill="{bg}"/>'
                f'<text x="12" y="17" text-anchor="middle" font-size="14" '
                f'font-weight="bold" fill="{text_color}" font-family="sans-serif">{initial}</text>'
                f'</svg>')

    return (f'<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24">'
            f'<text x="12" y="16" text-anchor="middle" font-size="12" '
            f'fill="#888" font-family="sans-serif">?</text></svg>')


def _generate_badge(name, color, url, icon_source, output_path):
    """Generate a single standalone social badge SVG."""
    svg = svg_header(BADGE_W, BADGE_H)
    svg += f'  <rect width="{BADGE_W}" height="{BADGE_H}" rx="12" fill="{CARD_BG}" stroke="{color}" stroke-width="1.5"/>\n'
    # Icon centered
    icon_size = 32
    icon_x = (BADGE_W - icon_size) // 2
    icon_y = 8
    icon_svg = _build_icon(name, color, icon_source, icon_size)
    svg += f'  <g transform="translate({icon_x}, {icon_y})">\n'
    svg += f'    {icon_svg}\n'
    svg += f'  </g>\n'
    # Label
    label_y = BADGE_H - 6
    display = name if len(name) <= 12 else name[:10] + ".."
    svg += f'  <text x="{BADGE_W // 2}" y="{label_y}" font-size="8" font-family="Segoe UI, sans-serif" fill="{TEXT}" text-anchor="middle">{display}</text>\n'
    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)


def generate_all_socials(assets_dir):
    """Generate all individual social badge SVGs."""
    for name, color, url, icon_source, filename in SOCIALS:
        path = os.path.join(assets_dir, filename)
        _generate_badge(name, color, url, icon_source, path)
        print(f"  ✓ {name:16s} → assets/{filename}")

    # Also return the list for README generation
    return SOCIALS


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    generate_all_socials(assets)
