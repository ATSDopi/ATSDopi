"""
Generate a social links SVG card with icons for each platform.
All icons are hand-drawn SVG — no external icon libraries.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, CARD_BG, BORDER, TEXT, TEXT_DIM, PURPLE, CYAN, INDIGO

BADGE_W = 48
BADGE_H = 48
GAP = 10

# Social platform definitions: (name, color, icon_svg, url)
SOCIALS = [
    ("guns.lol", "#a333d8",
     '<circle cx="12" cy="12" r="9" fill="none" stroke="#a333d8" stroke-width="1.5"/><path d="M8 10l4 4 4-4" stroke="#a333d8" stroke-width="2" fill="none"/><circle cx="12" cy="7" r="1.5" fill="#a333d8"/>',
     "https://guns.lol/atsdopi"),

    ("Discord", "#5865f2",
     '<path d="M19 5c-2-1-4-1.5-6-1.5S9 4 7 5c-1 3-1.5 6-1.5 9c1.5 1 3 1.5 4.5 2l1-2c-0.5-0.2-1-0.5-1.5-0.8c0.2-0.1 0.3-0.2 0.5-0.3c2 1 4 1 6 0c0.2 0.1 0.3 0.2 0.5 0.3c-0.5 0.3-1 0.6-1.5 0.8l1 2c1.5-0.5 3-1 4.5-2c0-3-0.5-6-1.5-9z" fill="#5865f2"/><circle cx="9.5" cy="11" r="1.2" fill="white"/><circle cx="14.5" cy="11" r="1.2" fill="white"/>',
     "https://discord.com/users/704717426729943070"),

    ("Instagram", "#e1306c",
     '<rect x="4" y="4" width="16" height="16" rx="5" fill="none" stroke="#e1306c" stroke-width="1.5"/><circle cx="12" cy="12" r="4" fill="none" stroke="#e1306c" stroke-width="1.5"/><circle cx="17" cy="7" r="1.2" fill="#e1306c"/>',
     "https://instagram.com/0._ats_.0"),

    ("Frost", "#00b4d8",
     '<path d="M12 2l-3 6h2v4l-4 2 4 2v4h-2l3 6 3-6h-2v-4l4-2-4-2V8h2z" fill="#00b4d8"/>',
     "https://www.frostapp.net/"),

    ("ATS Pro", "#7287fd",
     '<rect x="4" y="6" width="16" height="12" rx="2" fill="none" stroke="#7287fd" stroke-width="1.5"/><text x="12" y="16" text-anchor="middle" font-size="8" font-weight="bold" fill="#7287fd" font-family="monospace">ATS</text>',
     "https://www.atspro.fr/"),

    ("Email", "#ea4335",
     '<rect x="3" y="6" width="18" height="12" rx="2" fill="none" stroke="#ea4335" stroke-width="1.5"/><path d="M3 7l9 6 9-6" stroke="#ea4335" stroke-width="1.5" fill="none"/>',
     "mailto:atsprofessional67@gmail.com"),

    ("Potion", "#9b59b6",
     '<path d="M9 3h6v3l-2 4v8c0 2-1 3-3 3s-3-1-3-3v-8L9 6z" fill="none" stroke="#9b59b6" stroke-width="1.5"/><path d="M9 10h6" stroke="#9b59b6" stroke-width="1"/>',
     "https://www.potiongang.fr/"),

    ("Buy Me Coffee", "#ffdd00",
     '<path d="M6 8h12l-1 10c-.2 1.5-1.5 2.5-3 2.5H10c-1.5 0-2.8-1-3-2.5z" fill="none" stroke="#ffdd00" stroke-width="1.5"/><path d="M6 8h12v-2H6z" fill="#ffdd00" opacity="0.3"/><path d="M18 10h2c1 0 2 1 2 2s-1 2-2 2h-2" stroke="#ffdd00" stroke-width="1.5" fill="none"/>',
     "https://buymeacoffee.com/ats_dopi"),
]


def _social_badge(x, y, name, color, icon_svg, url):
    """Generate a single social badge with a clickable link."""
    svg = f'  <a href="{url}" target="_blank" rel="noopener noreferrer">\n'
    svg += f'  <g transform="translate({x}, {y})">\n'
    # Rounded square background
    svg += f'    <rect width="{BADGE_W}" height="{BADGE_H}" rx="10" fill="{CARD_BG}" stroke="{color}" stroke-width="1.5"/>\n'
    # Icon centered
    icon_size = 28
    icon_x = (BADGE_W - icon_size) // 2
    icon_y = (BADGE_H - icon_size) // 2 - 4
    svg += f'    <svg x="{icon_x}" y="{icon_y}" width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24">{icon_svg}</svg>\n'
    # Label
    label_y = BADGE_H - 6
    display = name if len(name) <= 12 else name[:10] + ".."
    svg += f'    <text x="{BADGE_W // 2}" y="{label_y}" font-size="8" font-family="Segoe UI, sans-serif" fill="{TEXT}" text-anchor="middle">{display}</text>\n'
    svg += '  </g>\n'
    svg += '  </a>\n'
    return svg


def generate_socials(socials, output_path):
    """Generate the social links SVG."""
    per_row = min(len(socials), 8)
    rows = (len(socials) + per_row - 1) // per_row

    total_w = per_row * BADGE_W + (per_row - 1) * GAP + 20
    total_h = rows * BADGE_H + (rows - 1) * GAP + 20

    svg = svg_header(total_w, total_h)
    svg += f'  <rect width="{total_w}" height="{total_h}" fill="none"/>\n'

    for i, (name, color, icon, url) in enumerate(socials):
        col = i % per_row
        row = i // per_row
        x = 10 + col * (BADGE_W + GAP)
        y = 10 + row * (BADGE_H + GAP)
        svg += _social_badge(x, y, name, color, icon, url)

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Social links ({len(socials)} platforms) → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    generate_socials(SOCIALS, os.path.join(assets, "socials.svg"))
