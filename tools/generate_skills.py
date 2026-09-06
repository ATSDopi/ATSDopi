"""
Generate custom skill icon badges as SVG using REAL brand logos.
Logos are fetched from simpleicons.org and devicon.dev and stored in icon_paths.json.
- simpleicons: single path with brand color fill
- devicon: full SVG content (preserves gradients, multiple paths, defs)
IDs in devicon SVGs are namespaced to avoid conflicts.
No hand-drawn icons — only official brand paths.
"""

import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, CARD_BG, BORDER, TEXT, TEXT_DIM

BADGE_W = 56
BADGE_H = 56
GAP = 8

# Load real icon paths
_ICONS_FILE = os.path.join(os.path.dirname(__file__), "icon_paths.json")
with open(_ICONS_FILE, "r", encoding="utf-8") as f:
    ICON_DATA = json.load(f)

# Fallback for Lightroom (not available in any icon library)
TEXT_FALLBACKS = {
    "Lightroom": ("#31a8ff", "Lr"),
}

# Tech groups for display
SKILL_GROUPS = [
    ["Python", "TypeScript", "JavaScript", "C", "C++", "C#", "Java", "PHP", "Rust", "Swift", "Kotlin"],
    ["HTML5", "React", "Next.js", "Node.js", "Electron", "WordPress", "Android"],
    ["MySQL", "PostgreSQL", "Firebase", "Docker", "PowerShell"],
    ["Figma", "Photoshop", "Lightroom", "After Effects", "Arduino"],
]


def _namespace_ids(svg_content, prefix):
    """Make all id= and url(#...) references unique by prefixing."""
    # Find all id="xxx" and replace with id="prefix_xxx"
    ids = re.findall(r'id="([^"]+)"', svg_content)
    for old_id in ids:
        new_id = f"{prefix}_{old_id}"
        svg_content = svg_content.replace(f'id="{old_id}"', f'id="{new_id}"')
        svg_content = svg_content.replace(f'url(#{old_id})', f'url(#{new_id})')
        svg_content = svg_content.replace(f'href="#{old_id}"', f'href="#{new_id}"')
    return svg_content


def _build_icon_svg(tech_name, icon_size):
    """Build an SVG fragment for a tech icon using real brand paths."""
    # Check text fallbacks first
    if tech_name in TEXT_FALLBACKS:
        color, label = TEXT_FALLBACKS[tech_name]
        return (f'<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24">'
                f'<rect x="2" y="2" width="20" height="20" rx="4" fill="{color}"/>'
                f'<text x="12" y="16" text-anchor="middle" font-size="11" '
                f'font-weight="bold" fill="white" font-family="sans-serif">{label}</text></svg>')

    if tech_name not in ICON_DATA:
        return (f'<svg width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24">'
                f'<text x="12" y="16" text-anchor="middle" font-size="10" '
                f'fill="#888" font-family="sans-serif">?</text></svg>')

    data = ICON_DATA[tech_name]
    color = data["color"]

    if data["source"] == "simpleicons":
        # Single path with brand color
        viewBox = data["viewBox"]
        d = data["path_d"]
        fill = "#ffffff" if color == "#ffffff" else color
        return (f'<svg width="{icon_size}" height="{icon_size}" viewBox="{viewBox}" '
                f'xmlns="http://www.w3.org/2000/svg">'
                f'<path d="{d}" fill="{fill}"/></svg>')

    else:  # devicon — embed full SVG content with namespaced IDs
        full_svg = data["full_svg"]
        # Create a safe prefix from tech name
        prefix = re.sub(r'[^a-zA-Z0-9]', '', tech_name)
        # Namespace all IDs to avoid conflicts
        full_svg = _namespace_ids(full_svg, prefix)
        # Replace width/height to fit our icon_size
        fixed = re.sub(r'width="[^"]*"', f'width="{icon_size}"', full_svg, count=1)
        fixed = re.sub(r'height="[^"]*"', f'height="{icon_size}"', fixed, count=1)
        return fixed


def _badge_svg(x, y, tech_name):
    """Generate a single skill badge with real logo."""
    color = "#888"
    if tech_name in ICON_DATA:
        color = ICON_DATA[tech_name]["color"]
    elif tech_name in TEXT_FALLBACKS:
        color = TEXT_FALLBACKS[tech_name][0]

    svg = f'  <g transform="translate({x}, {y})">\n'
    # Rounded square background
    svg += f'    <rect width="{BADGE_W}" height="{BADGE_H}" rx="10" fill="{CARD_BG}" stroke="{color}" stroke-width="1.5"/>\n'
    # Real icon centered
    icon_size = 32
    icon_x = (BADGE_W - icon_size) // 2
    icon_y = 6
    icon_svg = _build_icon_svg(tech_name, icon_size)
    # Position the icon
    svg += f'    <g transform="translate({icon_x}, {icon_y})">\n'
    svg += f'      {icon_svg}\n'
    svg += f'    </g>\n'
    # Label below icon
    label_y = BADGE_H - 7
    display = tech_name if len(tech_name) <= 11 else tech_name[:9] + ".."
    svg += f'    <text x="{BADGE_W // 2}" y="{label_y}" font-size="9" font-family="Segoe UI, sans-serif" fill="{TEXT}" text-anchor="middle">{display}</text>\n'
    svg += '  </g>\n'
    return svg


def generate_skills(groups, output_path):
    """Generate the skills SVG from a list of groups."""
    # Calculate layout
    max_row_len = max(len(g) for g in groups) if groups else 0
    total_w = max_row_len * BADGE_W + (max_row_len - 1) * GAP + 20
    total_h = len(groups) * BADGE_H + (len(groups) - 1) * GAP * 2 + 20

    svg = svg_header(total_w, total_h)
    svg += f'  <rect width="{total_w}" height="{total_h}" fill="none"/>\n'

    for row_idx, group in enumerate(groups):
        for col_idx, tech_name in enumerate(group):
            x = 10 + col_idx * (BADGE_W + GAP)
            y = 10 + row_idx * (BADGE_H + GAP * 2)
            svg += _badge_svg(x, y, tech_name)

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    count = sum(len(g) for g in groups)
    print(f"  ✓ Skills badges ({count} techs, real logos) → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    generate_skills(SKILL_GROUPS, os.path.join(assets, "skills.svg"))
