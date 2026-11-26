"""
Generate custom neon-style status badge SVGs.
Creates for-the-badge style badges with brand colors and glow effects.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, xml_escape, PURPLE, CYAN, INDIGO

BADGE_H = 32
GAP = 8
# ~6.4px per char at 11px bold Segoe + horizontal padding per side
CHAR_W = 6.4
PAD = 10


def _badge_widths(label, value):
    """Per-section widths sized to the text (shields.io style)."""
    label_w = len(label) * CHAR_W + PAD * 2
    value_w = len(value) * CHAR_W + PAD * 2
    return label_w, value_w


def _badge_svg(x, y, idx, label, value, color):
    """Generate a single for-the-badge style badge.

    The left tint section is a square rect clipped to the badge outline —
    its right edge stays perfectly straight, no overlapping-pill artifact.
    """
    clip = f"badgeClip{idx}"
    label_w, value_w = _badge_widths(label, value)
    badge_w = label_w + value_w
    svg = f'  <g transform="translate({x}, {y})">\n'
    svg += (f'    <clipPath id="{clip}">'
            f'<rect width="{badge_w}" height="{BADGE_H}" rx="4"/></clipPath>\n')
    # Background + border
    svg += f'    <rect width="{badge_w}" height="{BADGE_H}" rx="4" fill="#0d1117" stroke="{color}" stroke-width="1"/>\n'
    # Left section (label) — clipped square, only left corners get rounded
    svg += (f'    <rect width="{label_w:.1f}" height="{BADGE_H}" fill="{color}" '
            f'opacity="0.15" clip-path="url(#{clip})"/>\n')
    # Divider
    svg += (f'    <line x1="{label_w:.1f}" y1="0.5" x2="{label_w:.1f}" y2="{BADGE_H - 0.5}" '
            f'stroke="{color}" stroke-width="1" opacity="0.5"/>\n')
    # Label text
    svg += f'    <text x="{label_w / 2:.1f}" y="21" font-size="11" font-family="Segoe UI, sans-serif" font-weight="bold" fill="{color}" text-anchor="middle">{xml_escape(label)}</text>\n'
    # Value text
    svg += f'    <text x="{label_w + value_w / 2:.1f}" y="21" font-size="11" font-family="Segoe UI, sans-serif" font-weight="bold" fill="#c9d1d9" text-anchor="middle">{xml_escape(value)}</text>\n'
    svg += '  </g>\n'
    return svg


def generate_badges(badge_defs, output_path):
    """
    Generate a row of badges.
    badge_defs: list of (label, value, color)
    """
    widths = [sum(_badge_widths(l, v)) for l, v, _ in badge_defs]
    total_w = sum(widths) + (len(badge_defs) - 1) * GAP
    total_h = BADGE_H

    svg = svg_header(total_w, total_h)
    svg += f'  <rect width="{total_w}" height="{total_h}" fill="none"/>\n'

    x = 0
    for i, (label, value, color) in enumerate(badge_defs):
        svg += _badge_svg(x, 0, i, label, value, color)
        x += widths[i] + GAP

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
