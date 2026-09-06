"""
Generate custom skill icon badges as SVG.
Each technology gets a rounded badge with its brand color, a simple geometric icon,
and the technology name. No external icon libraries — all icons are hand-drawn SVG.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, CARD_BG, BORDER, TEXT, TEXT_DIM

BADGE_W = 56
BADGE_H = 56
GAP = 8

# Technology definitions: (name, color, icon_svg)
# Icons are drawn in a 24x24 viewBox
TECHS = [
    # ─── Languages ───
    ("Python", "#3776ab",
     '<path d="M12 3c-3 0-4 2-4 4v2h4v1H6c-2 0-3 2-3 4s1 3 3 3h2v-2c0-2 2-3 4-3h3c2 0 3-1 3-3V7c0-2-2-4-4-4h-2z" fill="#3776ab"/><path d="M12 21c3 0 4-2 4-4v-2h-4v-1h6c2 0 3-2 3-4s-1-3-3-3h-2v2c0 2-2 3-4 3H9c-2 0-3 1-3 3v4c0 2 2 4 4 4h2z" fill="#ffd43b"/>'),
    ("TypeScript", "#3178c6",
     '<text x="12" y="16" text-anchor="middle" font-size="10" font-weight="bold" fill="white" font-family="monospace">TS</text>'),
    ("JavaScript", "#f7df1e",
     '<text x="12" y="16" text-anchor="middle" font-size="10" font-weight="bold" fill="#323330" font-family="monospace">JS</text>'),
    ("C", "#a8b9cc",
     '<text x="12" y="17" text-anchor="middle" font-size="14" font-weight="bold" fill="white" font-family="monospace">C</text>'),
    ("C++", "#00599c",
     '<text x="12" y="16" text-anchor="middle" font-size="11" font-weight="bold" fill="white" font-family="monospace">C++</text>'),
    ("C#", "#9b4f96",
     '<text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="white" font-family="monospace">C#</text>'),
    ("Java", "#ed8b00",
     '<path d="M8 4h8v2H8z" fill="#ed8b00"/><path d="M7 6h10v12H7z" fill="none" stroke="#ed8b00" stroke-width="1.5"/><path d="M9 10h6M9 13h6M9 16h4" stroke="#ed8b00" stroke-width="1"/><circle cx="17" cy="5" r="2" fill="#ed8b00"/>'),
    ("PHP", "#777bb4",
     '<text x="12" y="16" text-anchor="middle" font-size="11" font-weight="bold" fill="white" font-family="monospace">php</text>'),
    ("Rust", "#dea584",
     '<circle cx="12" cy="12" r="8" fill="none" stroke="#dea584" stroke-width="1.5"/><path d="M8 12c2-2 6-2 8 0M9 9l3 3 3-3M9 15l3-3 3 3" stroke="#dea584" stroke-width="1" fill="none"/>'),
    ("Swift", "#fa7343",
     '<path d="M12 3l-7 7 7 7 7-7z" fill="none" stroke="#fa7343" stroke-width="1.5"/><path d="M12 7l-3 3 3 3 3-3z" fill="#fa7343"/>'),
    ("Kotlin", "#7f52ff",
     '<rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="#7f52ff" stroke-width="1.5"/><path d="M8 8l8 8M16 8l-8 8" stroke="#7f52ff" stroke-width="1"/>'),

    # ─── Web / Frontend ───
    ("HTML5", "#e34c26",
     '<text x="12" y="17" text-anchor="middle" font-size="12" font-weight="bold" fill="white" font-family="monospace">5</text>'),
    ("React", "#61dafb",
     '<circle cx="12" cy="12" r="2" fill="#61dafb"/><ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="#61dafb" stroke-width="1.5"/><ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="#61dafb" stroke-width="1.5" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" fill="none" stroke="#61dafb" stroke-width="1.5" transform="rotate(120 12 12)"/>'),
    ("Next.js", "#000000",
     '<circle cx="12" cy="12" r="9" fill="none" stroke="white" stroke-width="1.5"/><path d="M9 8v8M9 8l6 8M15 8v5" stroke="white" stroke-width="1.5" fill="none"/>'),
    ("Node.js", "#339933",
     '<path d="M12 2L3 7v10l9 5 9-5V7z" fill="none" stroke="#339933" stroke-width="1.5"/><path d="M12 6v12M8 9l4 2 4-2M8 15l4-2 4 2" stroke="#339933" stroke-width="1" fill="none"/>'),
    ("Electron", "#47848f",
     '<circle cx="12" cy="12" r="2" fill="#47848f"/><ellipse cx="12" cy="12" rx="9" ry="4" fill="none" stroke="#47848f" stroke-width="1"/><ellipse cx="12" cy="12" rx="9" ry="4" fill="none" stroke="#47848f" stroke-width="1" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="9" ry="4" fill="none" stroke="#47848f" stroke-width="1" transform="rotate(120 12 12)"/>'),
    ("WordPress", "#21759b",
     '<circle cx="12" cy="12" r="9" fill="none" stroke="#21759b" stroke-width="1.5"/><text x="12" y="16" text-anchor="middle" font-size="11" font-weight="bold" fill="white" font-family="monospace">W</text>'),
    ("Android", "#3ddc84",
     '<path d="M6 10c0-3 3-6 6-6s6 3 6 6v5H6z" fill="none" stroke="#3ddc84" stroke-width="1.5"/><circle cx="9" cy="11" r="1" fill="#3ddc84"/><circle cx="15" cy="11" r="1" fill="#3ddc84"/><path d="M7 4l1 2M17 4l-1 2" stroke="#3ddc84" stroke-width="1.5"/>'),

    # ─── Databases ───
    ("MySQL", "#00758f",
     '<rect x="4" y="6" width="16" height="12" rx="1" fill="none" stroke="#00758f" stroke-width="1.5"/><path d="M4 10h16M4 14h16" stroke="#00758f" stroke-width="1"/><circle cx="8" cy="8" r="0.8" fill="#00758f"/>'),
    ("PostgreSQL", "#336791",
     '<ellipse cx="12" cy="12" rx="8" ry="9" fill="none" stroke="#336791" stroke-width="1.5"/><path d="M8 10c2 2 6 2 8 0M8 14c2-2 6-2 8 0" stroke="#336791" stroke-width="1" fill="none"/>'),
    ("Firebase", "#ffca28",
     '<path d="M8 3l2 5 2-2 4 14H6z" fill="#ffca28" opacity="0.3"/><path d="M8 3l2 5 2-2 4 14H6z" fill="none" stroke="#ffca28" stroke-width="1.5"/><path d="M10 8l4 12" stroke="#ffca28" stroke-width="1"/>'),

    # ─── DevOps / Tools ───
    ("Docker", "#2496ed",
     '<rect x="4" y="12" width="3" height="3" fill="#2496ed"/><rect x="8" y="12" width="3" height="3" fill="#2496ed"/><rect x="12" y="12" width="3" height="3" fill="#2496ed"/><rect x="8" y="8" width="3" height="3" fill="#2496ed"/><rect x="12" y="8" width="3" height="3" fill="#2496ed"/><rect x="16" y="12" width="3" height="3" fill="#2496ed"/><path d="M3 16c2 2 16 2 18 0" stroke="#2496ed" stroke-width="1.5" fill="none"/>'),
    ("PowerShell", "#5391fe",
     '<text x="12" y="17" text-anchor="middle" font-size="14" font-weight="bold" fill="white" font-family="monospace">>_</text>'),

    # ─── Design / Creative ───
    ("Figma", "#f24e1e",
     '<circle cx="9" cy="6" r="3" fill="none" stroke="#f24e1e" stroke-width="1.5"/><circle cx="9" cy="12" r="3" fill="none" stroke="#a259ff" stroke-width="1.5"/><circle cx="9" cy="18" r="3" fill="none" stroke="#1abcfe" stroke-width="1.5"/><circle cx="15" cy="6" r="3" fill="none" stroke="#ff7262" stroke-width="1.5"/><circle cx="15" cy="12" r="3" fill="none" stroke="#0acf83" stroke-width="1.5"/>'),
    ("Photoshop", "#31a8ff",
     '<text x="12" y="16" text-anchor="middle" font-size="10" font-weight="bold" fill="white" font-family="monospace">Ps</text>'),
    ("Lightroom", "#31a8ff",
     '<text x="12" y="16" text-anchor="middle" font-size="10" font-weight="bold" fill="white" font-family="monospace">Lr</text>'),
    ("After Effects", "#cf96fd",
     '<text x="12" y="16" text-anchor="middle" font-size="9" font-weight="bold" fill="white" font-family="monospace">Ae</text>'),

    # ─── Hardware ───
    ("Arduino", "#00979d",
     '<rect x="3" y="8" width="18" height="10" rx="2" fill="none" stroke="#00979d" stroke-width="1.5"/><path d="M8 13h2M9 12v2M14 13h2" stroke="#00979d" stroke-width="1"/><circle cx="17" cy="11" r="1" fill="#00979d"/><circle cx="17" cy="15" r="1" fill="#00979d"/>'),
]


def _badge_svg(x, y, name, color, icon_svg):
    """Generate a single skill badge."""
    svg = f'  <g transform="translate({x}, {y})">\n'
    # Rounded square background
    svg += f'    <rect width="{BADGE_W}" height="{BADGE_H}" rx="10" fill="{CARD_BG}" stroke="{color}" stroke-width="1.5"/>\n'
    # Icon area (centered)
    icon_size = 30
    icon_x = (BADGE_W - icon_size) // 2
    icon_y = 6
    svg += f'    <svg x="{icon_x}" y="{icon_y}" width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24">{icon_svg}</svg>\n'
    # Label below icon
    label_y = BADGE_H - 7
    # Shorten label if too long
    display = name if len(name) <= 11 else name[:9] + ".."
    svg += f'    <text x="{BADGE_W // 2}" y="{label_y}" font-size="9" font-family="Segoe UI, sans-serif" fill="{TEXT}" text-anchor="middle">{display}</text>\n'
    svg += '  </g>\n'
    return svg


def generate_skills(groups, output_path):
    """
    Generate the skills SVG from a list of groups.
    Each group is a list of tech names. Groups are separated by a gap.
    """
    # Resolve tech names to definitions
    tech_map = {name: (color, icon) for name, color, icon in TECHS}

    # Calculate layout
    max_row_len = max(len(g) for g in groups) if groups else 0
    total_w = max_row_len * BADGE_W + (max_row_len - 1) * GAP + 20
    total_h = len(groups) * BADGE_H + (len(groups) - 1) * GAP * 2 + 20

    svg = svg_header(total_w, total_h)
    svg += f'  <rect width="{total_w}" height="{total_h}" fill="none"/>\n'

    for row_idx, group in enumerate(groups):
        for col_idx, tech_name in enumerate(group):
            if tech_name not in tech_map:
                print(f"  ⚠ Unknown tech: {tech_name}")
                continue
            color, icon = tech_map[tech_name]
            x = 10 + col_idx * (BADGE_W + GAP)
            y = 10 + row_idx * (BADGE_H + GAP * 2)
            svg += _badge_svg(x, y, tech_name, color, icon)

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Skills badges ({sum(len(g) for g in groups)} techs) → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)

    groups = [
        ["Python", "TypeScript", "JavaScript", "C", "C++", "C#", "Java", "PHP", "Rust", "Swift", "Kotlin"],
        ["HTML5", "React", "Next.js", "Node.js", "Electron", "WordPress", "Android"],
        ["MySQL", "PostgreSQL", "Firebase", "Docker", "PowerShell"],
        ["Figma", "Photoshop", "Lightroom", "After Effects", "Arduino"],
    ]
    generate_skills(groups, os.path.join(assets, "skills.svg"))
