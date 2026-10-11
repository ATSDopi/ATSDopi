"""
Generate an animated Pac-Man SVG on the contribution grid.
Pac-Man serpentines through the grid eating cells — each cell dims as he
passes over it, then relights when the chasing ghosts sweep through.
A moving "comet window" of darkness follows the pack. Pure SMIL.
"""

import sys
import os
import math
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, PURPLE, CYAN, INDIGO, GREEN, BORDER, CARD_BG, DARK_BG
from github_client import get_contributions

CELL = 12
CELL_GAP = 2
CELL_SIZE = CELL + CELL_GAP
GRID_ROWS = 7  # days (row 0 = Sunday, like GitHub)

EMPTY_CELL = "#21262d"   # visible empty cell (not the card bg — grid must read)
EATEN_CELL = "#0d1117"   # freshly eaten cell (darker than empty)

PAC_SIZE = 24       # 2× cell — reads as Pac-Man, not a triangle
GHOST_SIZE = 22
GHOST_TRAIL_S = 0.6   # delay between pacman and first ghost
GHOST_GAP_S = 0.55    # delay between each ghost
TAIL_S = 2.6          # cells stay eaten this long before relighting


def _level_color(count):
    """Map contribution count to a color level."""
    if count == 0:
        return EMPTY_CELL
    elif count <= 3:
        return "#0e4429"
    elif count <= 6:
        return "#006d32"
    elif count <= 9:
        return "#26a641"
    else:
        return "#39d353"


def _pacman_svg(size, mouth_open):
    """Draw Pac-Man facing right. mouth_open: 0 (closed) to 1 (fully open).
    Built as a full circle with the mouth wedge punched out in bg color —
    bulletproof vs arc-flag subtleties."""
    half_angle = math.radians(42 * mouth_open)

    cx, cy = size / 2, size / 2
    r = size / 2 - 0.5

    # Mouth wedge (opens right): center → upper lip → right-edge arc → lower lip
    mx = cx + (r + 1) * math.cos(half_angle)
    ty = cy - (r + 1) * math.sin(half_angle)
    by = cy + (r + 1) * math.sin(half_angle)
    mouth = (f"M{cx:.1f},{cy:.1f} L{mx:.1f},{ty:.1f} "
             f"A{r + 1:.1f},{r + 1:.1f} 0 0,1 {mx:.1f},{by:.1f} Z")

    eye_r = r * 0.13
    eye_x = cx + r * 0.15
    eye_y = cy - r * 0.45

    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#ffd83d" '
            f'stroke="#f0b800" stroke-width="0.6"/>'
            f'<path d="{mouth}" fill="{CARD_BG}"/>'
            f'<circle cx="{eye_x:.1f}" cy="{eye_y:.1f}" r="{eye_r:.1f}" fill="#1a1a1a"/>')


def _ghost_svg(size, color):
    """Draw a classic ghost silhouette (tall dome + 3-tooth skirt)."""
    cx, cy = size / 2, size / 2
    r = size / 2 - 0.5
    top_y = cy - r * 0.55          # dome apex above center
    skirt_y = cy + r * 0.85
    w = 2 * r
    seg = w / 6

    # Dome + sides + 3-tooth zigzag skirt
    path = (
        f"M{cx - r:.1f},{skirt_y:.1f} "
        f"L{cx - r:.1f},{top_y + r * 0.3:.1f} "
        f"A{r},{r * 0.95:.1f} 0 0,1 {cx + r:.1f},{top_y + r * 0.3:.1f} "
        f"L{cx + r:.1f},{skirt_y:.1f} "
        f"L{cx + seg:.1f},{skirt_y - r * 0.3:.1f} "
        f"L{cx:.1f},{skirt_y:.1f} "
        f"L{cx - seg:.1f},{skirt_y - r * 0.3:.1f} "
        f"Z"
    )

    eye_r = r * 0.3
    pupil_r = r * 0.13
    eye_y = cy - r * 0.15

    return (
        f'<path d="{path}" fill="{color}"/>'
        f'<ellipse cx="{cx - r * 0.36:.1f}" cy="{eye_y:.1f}" rx="{eye_r * 0.8:.1f}" ry="{eye_r:.1f}" fill="white"/>'
        f'<circle cx="{cx - r * 0.36 + pupil_r:.1f}" cy="{eye_y:.1f}" r="{pupil_r:.1f}" fill="#2121ff"/>'
        f'<ellipse cx="{cx + r * 0.36:.1f}" cy="{eye_y:.1f}" rx="{eye_r * 0.8:.1f}" ry="{eye_r:.1f}" fill="white"/>'
        f'<circle cx="{cx + r * 0.36 + pupil_r:.1f}" cy="{eye_y:.1f}" r="{pupil_r:.1f}" fill="#2121ff"/>'
    )


def generate_pacman(username, output_path, contribs=None):
    """Generate the animated Pac-Man SVG on the contribution grid."""
    if contribs is None:
        print(f"  Fetching contributions for pacman ({username})...")
        contribs = get_contributions(username)
    days = contribs["days"]

    if days:
        sorted_days = sorted(days, key=lambda d: d["date"])
        first = datetime.strptime(sorted_days[0]["date"], "%Y-%m-%d")
        last = datetime.strptime(sorted_days[-1]["date"], "%Y-%m-%d")
        start_date = first - timedelta(days=(first.weekday() + 1) % 7)
        grid_cols = (last - start_date).days // 7 + 1

        date_map = {d["date"]: d["contributionCount"] for d in sorted_days}
        grid = [[0] * grid_cols for _ in range(GRID_ROWS)]
        for col in range(grid_cols):
            for row in range(GRID_ROWS):
                d = start_date + timedelta(days=col * 7 + row)
                key = d.strftime("%Y-%m-%d")
                grid[row][col] = date_map.get(key, 0)
    else:
        grid_cols = 52
        grid = [[0] * grid_cols for _ in range(GRID_ROWS)]

    # SVG dimensions
    offset_x = 10
    offset_y = 10
    grid_w = grid_cols * CELL_SIZE
    grid_h = GRID_ROWS * CELL_SIZE
    W = grid_w + 20
    H = grid_h + 20

    svg = svg_header(W, H)
    svg += f'  <rect width="{W}" height="{H}" fill="{CARD_BG}" rx="8"/>\n'

    # ─── Serpentine path through cell centers (col 0 top→down, col 1 bottom→up…) ───
    # Cell visit index maps each grid position to its time on the path
    visit_index = {}
    path_points = []
    for col in range(grid_cols):
        rows = range(GRID_ROWS) if col % 2 == 0 else range(GRID_ROWS - 1, -1, -1)
        for row in rows:
            cx = offset_x + col * CELL_SIZE + CELL / 2
            cy = offset_y + row * CELL_SIZE + CELL / 2
            path_points.append((cx, cy))
            visit_index[(row, col)] = len(path_points) - 1

    total_points = len(path_points)
    dur = max(total_points * 0.055, 10)
    tail_frac = TAIL_S / dur

    # ─── Grid cells — each dims when Pac-Man passes, relights after the tail ───
    for row in range(GRID_ROWS):
        for col in range(grid_cols):
            orig = _level_color(grid[row][col])
            x = offset_x + col * CELL_SIZE
            y = offset_y + row * CELL_SIZE
            idx = visit_index[(row, col)]
            t_eat = max(idx / total_points, 0.0001)
            t_restore = min(max(t_eat + tail_frac, t_eat + 0.0001), 1.0)
            svg += (f'  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{orig}">'
                    f'<animate attributeName="fill" dur="{dur:.2f}s" repeatCount="indefinite" '
                    f'values="{orig};{EATEN_CELL};{orig}" '
                    f'keyTimes="0;{t_eat:.5f};{t_restore:.5f}" '
                    f'calcMode="discrete"/>'
                    f'</rect>\n')

    path_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in path_points)
    svg += f'  <path id="pacPath" d="{path_d}" fill="none" stroke="none"/>\n'

    # ─── Pac-Man (chomping mouth via open/closed swap) ───
    pac_open = _pacman_svg(PAC_SIZE, 1.0)
    pac_closed = _pacman_svg(PAC_SIZE, 0.08)
    svg += f'  <g filter="url(#glowStrong)">\n'
    svg += f'    <animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto">\n'
    svg += f'      <mpath href="#pacPath"/>\n'
    svg += f'    </animateMotion>\n'
    svg += f'    <g transform="translate({-PAC_SIZE / 2:.1f}, {-PAC_SIZE / 2:.1f})">\n'
    svg += f'      <svg width="{PAC_SIZE}" height="{PAC_SIZE}" viewBox="0 0 {PAC_SIZE} {PAC_SIZE}">\n'
    svg += f'        <g opacity="1">{pac_open}\n'
    svg += f'          <animate attributeName="opacity" dur="0.28s" repeatCount="indefinite" values="1;0;1" keyTimes="0;0.5;1" calcMode="discrete"/>\n'
    svg += f'        </g>\n'
    svg += f'        <g opacity="0">{pac_closed}\n'
    svg += f'          <animate attributeName="opacity" dur="0.28s" repeatCount="indefinite" values="0;1;0" keyTimes="0;0.5;1" calcMode="discrete"/>\n'
    svg += f'        </g>\n'
    svg += f'      </svg>\n'
    svg += f'    </g>\n'
    svg += f'  </g>\n'

    # ─── Ghosts chasing behind (Blinky, Pinky, Inky, Clyde) ───
    ghost_colors = ["#ff3b3b", "#ffb8de", "#00e8ff", "#ffb852"]

    for i, color in enumerate(ghost_colors):
        delay = GHOST_TRAIL_S + i * GHOST_GAP_S
        svg += f'  <g filter="url(#glow)" opacity="0.95">\n'
        svg += f'    <animateMotion dur="{dur}s" repeatCount="indefinite" begin="-{delay}s" rotate="auto">\n'
        svg += f'      <mpath href="#pacPath"/>\n'
        svg += f'    </animateMotion>\n'
        svg += f'    <g transform="translate({-GHOST_SIZE / 2:.1f}, {-GHOST_SIZE / 2:.1f})">\n'
        svg += f'      <svg width="{GHOST_SIZE}" height="{GHOST_SIZE}" viewBox="0 0 {GHOST_SIZE} {GHOST_SIZE}">\n'
        svg += f'        {_ghost_svg(GHOST_SIZE, color)}\n'
        svg += f'      </svg>\n'
        svg += f'    </g>\n'
        svg += f'  </g>\n'

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Pac-Man animation → {output_path} ({total_points} path points, {dur:.1f}s loop)")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    generate_pacman(username, os.path.join(assets, "pacman.svg"))
