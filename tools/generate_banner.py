"""
Generate animated header and footer banner SVGs.
Uses SMIL <animate> for wave motion — works in GitHub's <img> rendering.
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import (
    svg_header, svg_footer, INDIGO, PURPLE, CYAN, DARK_BG, TEXT
)

WIDTH = 900
HEADER_HEIGHT = 220
FOOTER_HEIGHT = 120


def _wave_path(width, height, offset, amplitude=18, wavelength=200):
    """Generate a sine wave path string."""
    points = []
    steps = 80
    for i in range(steps + 1):
        x = (i / steps) * width
        y = height + math.sin((x / wavelength) * 2 * math.pi + offset) * amplitude
        points.append(f"{x:.1f},{y:.1f}")
    # Close the path to fill the bottom
    path = f"M0,{height} L" + " L".join(points) + f" L{width},{height + amplitude * 2} L0,{height + amplitude * 2} Z"
    return path


def generate_header(username, subtitle, output_path):
    """Generate the animated header banner."""
    svg = svg_header(WIDTH, HEADER_HEIGHT)

    # Background gradient fill
    svg += f'  <rect width="{WIDTH}" height="{HEADER_HEIGHT}" fill="{DARK_BG}"/>\n'

    # Animated gradient waves at the bottom
    wave_colors = [INDIGO, PURPLE, CYAN]
    wave_opacities = [0.15, 0.25, 0.35]
    wave_amps = [22, 18, 14]
    wave_speeds = [8, 6, 4]
    base_y = HEADER_HEIGHT - 60

    for i in range(3):
        wave_id = f"wave{i}"
        # Initial path
        path0 = _wave_path(WIDTH, base_y + i * 12, 0, wave_amps[i], 200 + i * 50)
        path1 = _wave_path(WIDTH, base_y + i * 12, math.pi, wave_amps[i], 200 + i * 50)
        svg += f'  <path id="{wave_id}" d="{path0}" fill="{wave_colors[i]}" opacity="{wave_opacities[i]}">\n'
        svg += f'    <animate attributeName="d" dur="{wave_speeds[i]}s" repeatCount="indefinite"\n'
        svg += f'      values="{path0};{path1};{path0}"/>\n'
        svg += f'  </path>\n'

    # Username text with glow
    svg += f'  <text x="{WIDTH // 2}" y="85" font-size="72" font-weight="bold" '
    svg += f'font-family="Segoe UI, Helvetica, Arial, sans-serif" '
    svg += f'fill="#ffffff" text-anchor="middle" filter="url(#glowStrong)">'
    svg += f'{username}</text>\n'

    # Subtitle with fade-in animation
    svg += f'  <text x="{WIDTH // 2}" y="130" font-size="20" '
    svg += f'font-family="Segoe UI, Helvetica, Arial, sans-serif" '
    svg += f'fill="{CYAN}" text-anchor="middle" opacity="0">\n'
    svg += f'    {subtitle}\n'
    svg += f'    <animate attributeName="opacity" from="0" to="1" dur="2s" '
    svg += f'begin="0.5s" fill="freeze"/>\n'
    svg += f'  </text>\n'

    # Decorative line under subtitle
    svg += f'  <line x1="{WIDTH // 2 - 120}" y1="150" x2="{WIDTH // 2 + 120}" y2="150" '
    svg += f'stroke="{PURPLE}" stroke-width="2" opacity="0">\n'
    svg += f'    <animate attributeName="opacity" from="0" to="0.6" dur="1.5s" '
    svg += f'begin="1s" fill="freeze"/>\n'
    svg += f'    <animate attributeName="x1" from="{WIDTH // 2}" to="{WIDTH // 2 - 120}" '
    svg += f'dur="1.5s" begin="1s" fill="freeze"/>\n'
    svg += f'    <animate attributeName="x2" from="{WIDTH // 2}" to="{WIDTH // 2 + 120}" '
    svg += f'dur="1.5s" begin="1s" fill="freeze"/>\n'
    svg += f'  </line>\n'

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Header banner → {output_path}")


def generate_footer(output_path):
    """Generate the animated footer banner."""
    svg = svg_header(WIDTH, FOOTER_HEIGHT)

    svg += f'  <rect width="{WIDTH}" height="{FOOTER_HEIGHT}" fill="{DARK_BG}"/>\n'

    # Animated waves at the top (mirrored)
    wave_colors = [CYAN, PURPLE, INDIGO]
    wave_opacities = [0.35, 0.25, 0.15]
    wave_amps = [14, 18, 22]
    wave_speeds = [4, 6, 8]

    for i in range(3):
        wave_id = f"fwave{i}"
        path0 = _wave_path(WIDTH, 40 + i * 12, 0, wave_amps[i], 200 + i * 50)
        path1 = _wave_path(WIDTH, 40 + i * 12, math.pi, wave_amps[i], 200 + i * 50)
        svg += f'  <path id="{wave_id}" d="{path0}" fill="{wave_colors[i]}" opacity="{wave_opacities[i]}">\n'
        svg += f'    <animate attributeName="d" dur="{wave_speeds[i]}s" repeatCount="indefinite"\n'
        svg += f'      values="{path0};{path1};{path0}"/>\n'
        svg += f'  </path>\n'

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Footer banner → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    subtitle = sys.argv[2] if len(sys.argv) > 2 else "Full-Stack • Backend • Cybersecurity"
    generate_header(username, subtitle, os.path.join(assets, "banner.svg"))
    generate_footer(os.path.join(assets, "footer.svg"))
