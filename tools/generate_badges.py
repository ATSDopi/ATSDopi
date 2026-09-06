"""
Generate custom neon-style status badge SVGs.
Creates for-the-badge style badges with brand colors and glow effects.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, PURPLE, CYAN, INDIGO

BADGE_W = 160
BADGE_H = 32
GAP = 8


def _badge_svg(x, y, label, value, color):
    """Generate a single for-the-badge style badge."""
    svg = f'  <g transform="translate({x}, {y})">\n'
    # Background
    svg += f'    <rect width="{BADGE_W}" height="{BADGE_H}" rx="4" fill="#0d1117" stroke="{color}" stroke-width="1"/>\n'
    # Left section (label)
    label_w = BADGE_W * 0.55
    svg += f'    <rect width="{label_w}" height="{BADGE_H}" rx="4" fill="{color}" opacity="0.15"/>\n'
    # Divider
    svg += f'    <line x1="{label_w}" y1="0" x2="{label_w}" y2="{BADGE_H}" stroke="{color}" stroke-width="1" opacity="0.5"/>\n'
    # Label text
    svg += f'    <text x="{label_w / 2}" y="21" font-size="11" font-family="Segoe UI, sans-serif" font-weight="bold" fill="{color}" text-anchor="middle">{label}</text>\n'
    # Value text
    svg += f'    <text x="{label_w + (BADGE_W - label_w) / 2}" y="21" font-size="11" font-family="Segoe UI, sans-serif" font-weight="bold" fill="#c9d1d9" text-anchor="middle">{value}</text>\n'
    svg += '  </g>\n'
    return svg


def generate_badges(badge_defs, output_path):
    """
    Generate a row of badges.
    badge_defs: list of (label, value, color)
    """
    total_w = len(badge_defs) * BADGE_W + (len(badge_defs) - 1) * GAP
    total_h = BADGE_H

    svg = svg_header(total_w, total_h)
    svg += f'  <rect width="{total_w}" height="{total_h}" fill="none"/>\n'

    for i, (label, value, color) in enumerate(badge_defs):
        x = i * (BADGE_W + GAP)
        svg += _badge_svg(x, 0, label, value, color)

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Badges ({len(badge_defs)}) → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)

    badges = [
        ("Status", "Online", CYAN),
        ("Focus", "CTF & Security", PURPLE),
        ("Role", "Student", INDIGO),
    ]
    generate_badges(badges, os.path.join(assets, "badges.svg"))
