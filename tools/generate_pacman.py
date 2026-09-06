"""
Generate an animated Pac-Man SVG on the contribution grid.
Pac-Man moves across the grid eating dots (contributions).
Ghosts chase behind. Uses SMIL animateMotion.
"""

import sys
import os
import math
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, PURPLE, CYAN, INDIGO, GREEN, BORDER, CARD_BG
from github_client import get_contributions

CELL = 12
CELL_GAP = 2
CELL_SIZE = CELL + CELL_GAP
GRID_COLS = 52  # weeks
GRID_ROWS = 7  # days


def _level_color(count):
    """Map contribution count to a color level."""
    if count == 0:
        return "#161b22"
    elif count <= 3:
        return "#0e4429"
    elif count <= 6:
        return "#006d32"
    elif count <= 9:
        return "#26a641"
    else:
        return "#39d353"


def _pacman_svg(size, mouth_open):
    """Draw Pac-Man facing right. mouth_open: 0 (closed) to 1 (fully open)."""
    # Pac-Man is a circle with a wedge cut out for the mouth
    # mouth angle: 0 to 50 degrees (half-angle 0 to 25)
    half_angle = 25 * mouth_open  # degrees
    angle_rad = math.radians(half_angle)

    # Center of pac-man
    cx, cy = size / 2, size / 2
    r = size / 2 - 1

    # Mouth points: top and bottom of the wedge
    # Mouth opens to the right
    top_x = cx + r * math.cos(angle_rad)
    top_y = cy - r * math.sin(angle_rad)
    bot_x = cx + r * math.cos(angle_rad)
    bot_y = cy + r * math.sin(angle_rad)

    # Path: move to center, line to top, arc to bottom (going clockwise through left), back to center
    path = (f"M{cx:.1f},{cy:.1f} "
            f"L{top_x:.1f},{top_y:.1f} "
            f"A{r},{r} 0 1,1 {bot_x:.1f},{bot_y:.1f} "
            f"Z")

    # Eye
    eye_x = cx - r * 0.1
    eye_y = cy - r * 0.45
    eye_r = r * 0.12

    return f'<path d="{path}" fill="#ffff00" stroke="#ffcc00" stroke-width="0.5"/><circle cx="{eye_x:.1f}" cy="{eye_y:.1f}" r="{eye_r:.1f}" fill="#000"/>'


def _ghost_svg(size, color):
    """Draw a ghost (Blinky-style) facing right."""
    cx, cy = size / 2, size / 2
    r = size / 2 - 1
    # Ghost body: semicircle top, wavy bottom
    # Top arc
    top = f"M{cx - r:.1f},{cy:.1f} A{r},{r} 0 0,1 {cx + r:.1f},{cy:.1f}"
    # Bottom wavy edge (3 bumps)
    w = 2 * r
    bump_h = r * 0.25
    b1_x = cx - r + w / 6
    b2_x = cx - r + w / 2
    b3_x = cx - r + 5 * w / 6
    bottom = (f" L{cx + r:.1f},{cy + r * 0.8:.1f}"
              f" L{b3_x:.1f},{cy + r * 0.8 - bump_h:.1f}"
              f" L{b3_x - w / 12:.1f},{cy + r * 0.8:.1f}"
              f" L{b2_x:.1f},{cy + r * 0.8 - bump_h:.1f}"
              f" L{b2_x - w / 12:.1f},{cy + r * 0.8:.1f}"
              f" L{b1_x:.1f},{cy + r * 0.8 - bump_h:.1f}"
              f" L{b1_x - w / 12:.1f},{cy + r * 0.8:.1f}"
              f" L{cx - r:.1f},{cy + r * 0.8:.1f} Z")
    path = top + bottom

    # Eyes (white with blue pupils looking right)
    eye_r = r * 0.22
    eye_y = cy - r * 0.15
    pupil_r = eye_r * 0.5
    pupil_offset = eye_r * 0.4

    return (
        f'<path d="{path}" fill="{color}" stroke="{color}" stroke-width="0.5" opacity="0.95"/>'
        f'<circle cx="{cx - r * 0.35:.1f}" cy="{eye_y:.1f}" r="{eye_r:.1f}" fill="white"/>'
        f'<circle cx="{cx - r * 0.35 + pupil_offset:.1f}" cy="{eye_y:.1f}" r="{pupil_r:.1f}" fill="#0033ff"/>'
        f'<circle cx="{cx + r * 0.35:.1f}" cy="{eye_y:.1f}" r="{eye_r:.1f}" fill="white"/>'
        f'<circle cx="{cx + r * 0.35 + pupil_offset:.1f}" cy="{eye_y:.1f}" r="{pupil_r:.1f}" fill="#0033ff"/>'
    )


def generate_pacman(username, output_path):
    """Generate the animated Pac-Man SVG on the contribution grid."""
    print(f"  Fetching contributions for pacman ({username})...")
    contribs = get_contributions(username)
    days = contribs["days"]

    if not days:
        grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
    else:
        sorted_days = sorted(days, key=lambda d: d["date"])
        if sorted_days:
            first = datetime.strptime(sorted_days[0]["date"], "%Y-%m-%d")
            start_date = first - timedelta(days=first.weekday() + 1)
            if start_date.weekday() == 6:
                start_date = first
        else:
            start_date = datetime.now() - timedelta(days=364)

        date_map = {d["date"]: d["contributionCount"] for d in sorted_days}
        grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                d = start_date + timedelta(days=col * 7 + row)
                key = d.strftime("%Y-%m-%d")
                grid[row][col] = date_map.get(key, 0)

    # SVG dimensions
    grid_w = GRID_COLS * CELL_SIZE
    grid_h = GRID_ROWS * CELL_SIZE
    W = grid_w + 20
    H = grid_h + 20

    svg = svg_header(W, H)
    svg += f'  <rect width="{W}" height="{H}" fill="{CARD_BG}" rx="8"/>\n'

    # Draw the contribution grid + dots for contributions
    offset_x = 10
    offset_y = 10

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            count = grid[row][col]
            color = _level_color(count)
            x = offset_x + col * CELL_SIZE
            y = offset_y + row * CELL_SIZE
            svg += f'  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>\n'

    # ─── Pac-Man path: serpentine through the grid ───
    path_points = []
    for col in range(GRID_COLS):
        if col % 2 == 0:
            for row in range(GRID_ROWS):
                cx = offset_x + col * CELL_SIZE + CELL / 2
                cy = offset_y + row * CELL_SIZE + CELL / 2
                path_points.append((cx, cy))
        else:
            for row in range(GRID_ROWS - 1, -1, -1):
                cx = offset_x + col * CELL_SIZE + CELL / 2
                cy = offset_y + row * CELL_SIZE + CELL / 2
                path_points.append((cx, cy))

    path_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in path_points)
    total_points = len(path_points)
    dur = max(total_points * 0.06, 8)

    # Define the motion path
    svg += f'  <path id="pacPath" d="{path_d}" fill="none" stroke="none"/>\n'

    # ─── Pac-Man (with chomping mouth animation) ───
    pac_size = CELL + 4
    # We need to animate the mouth opening/closing
    # Use a <g> that follows the path, containing Pac-Man with animated mouth
    svg += f'  <g filter="url(#glow)">\n'
    svg += f'    <g>\n'
    svg += f'      <animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto">\n'
    svg += f'        <mpath href="#pacPath"/>\n'
    svg += f'      </animateMotion>\n'
    # Pac-Man body with chomping animation (scale the mouth wedge)
    # We'll use opacity swap between open and closed pac-man
    pac_open = _pacman_svg(pac_size, 1.0)
    pac_closed = _pacman_svg(pac_size, 0.1)
    svg += f'      <g transform="translate({-pac_size / 2:.1f}, {-pac_size / 2:.1f})">\n'
    svg += f'        <svg width="{pac_size}" height="{pac_size}" viewBox="0 0 {pac_size} {pac_size}">\n'
    svg += f'          <g opacity="1">{pac_open}\n'
    svg += f'            <animate attributeName="opacity" dur="0.3s" repeatCount="indefinite" values="1;0;1" keyTimes="0;0.5;1"/>\n'
    svg += f'          </g>\n'
    svg += f'          <g opacity="0">{pac_closed}\n'
    svg += f'            <animate attributeName="opacity" dur="0.3s" repeatCount="indefinite" values="0;1;0" keyTimes="0;0.5;1"/>\n'
    svg += f'          </g>\n'
    svg += f'        </svg>\n'
    svg += f'      </g>\n'
    svg += f'    </g>\n'
    svg += f'  </g>\n'

    # ─── Ghosts chasing Pac-Man ───
    ghost_colors = ["#ff0000", "#ffb8ff", "#00ffff", "#ffb852"]
    ghost_size = CELL + 2

    for i, color in enumerate(ghost_colors):
        delay = (i + 1) * 0.8
        svg += f'  <g filter="url(#glow)">\n'
        svg += f'    <g>\n'
        svg += f'      <animateMotion dur="{dur}s" repeatCount="indefinite" begin="-{delay}s" rotate="auto">\n'
        svg += f'        <mpath href="#pacPath"/>\n'
        svg += f'      </animateMotion>\n'
        svg += f'      <g transform="translate({-ghost_size / 2:.1f}, {-ghost_size / 2:.1f})">\n'
        svg += f'        <svg width="{ghost_size}" height="{ghost_size}" viewBox="0 0 {ghost_size} {ghost_size}">\n'
        svg += f'          {_ghost_svg(ghost_size, color)}\n'
        svg += f'        </svg>\n'
        svg += f'      </g>\n'
        svg += f'    </g>\n'
        svg += f'  </g>\n'

    # ─── Glowing dots trail (power pellets) ───
    for i in range(4):
        delay = (i + 5) * 0.5
        r = 3 - i * 0.4
        op = 0.4 - i * 0.08
        svg += f'  <circle r="{r:.1f}" fill="{CYAN}" opacity="{op:.2f}">\n'
        svg += f'    <animateMotion dur="{dur}s" repeatCount="indefinite" begin="-{delay}s">\n'
        svg += f'      <mpath href="#pacPath"/>\n'
        svg += f'    </animateMotion>\n'
        svg += f'  </circle>\n'

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Pac-Man animation → {output_path} ({total_points} path points, {dur:.1f}s loop)")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    generate_pacman(username, os.path.join(assets, "snake.svg"))
