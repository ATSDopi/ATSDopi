"""
Generate an animated snake SVG that slithers across the contribution grid.
The snake has a visible body (segmented), a head with eyes, and leaves a
glowing trail. Uses SMIL animateMotion for smooth movement.
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


def generate_snake(username, output_path):
    """Generate the animated snake SVG on the contribution grid."""
    print(f"  Fetching contributions for snake ({username})...")
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

    # Draw the contribution grid
    offset_x = 10
    offset_y = 10

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            count = grid[row][col]
            color = _level_color(count)
            x = offset_x + col * CELL_SIZE
            y = offset_y + row * CELL_SIZE
            svg += f'  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>\n'

    # Generate a snake path — serpentine weave through the grid
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

    # Build the motion path
    path_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in path_points)
    total_points = len(path_points)
    dur = max(total_points * 0.06, 8)

    # Define the snake path (invisible, used for animateMotion)
    svg += f'  <path id="snakePath" d="{path_d}" fill="none" stroke="none"/>\n'

    # ─── Snake body: 12 segments with gradient color and trailing effect ───
    snake_segments = 12
    base_radius = 6.5

    for i in range(snake_segments, -1, -1):
        # i=0 is the tail (smallest, most transparent), i=snake_segments is the head
        radius = base_radius * (0.3 + 0.7 * (i / snake_segments))
        # Color gradient from INDIGO (tail) to PURPLE (mid) to CYAN (head)
        if i < snake_segments * 0.3:
            color = INDIGO
            opacity = 0.4 + 0.4 * (i / (snake_segments * 0.3))
        elif i < snake_segments * 0.7:
            color = PURPLE
            opacity = 0.7 + 0.2 * ((i - snake_segments * 0.3) / (snake_segments * 0.4))
        else:
            color = CYAN
            opacity = 0.9 + 0.1 * ((i - snake_segments * 0.7) / (snake_segments * 0.3))

        begin_delay = (snake_segments - i) * 0.12

        svg += f'  <circle r="{radius:.1f}" fill="{color}" opacity="{opacity:.2f}" filter="url(#glow)">\n'
        svg += f'    <animateMotion dur="{dur}s" repeatCount="indefinite" begin="-{begin_delay}s" rotate="auto">\n'
        svg += f'      <mpath href="#snakePath"/>\n'
        svg += f'    </animateMotion>\n'
        svg += f'  </circle>\n'

    # ─── Snake head: larger circle with eyes ───
    svg += f'  <g filter="url(#glowStrong)">\n'
    # Head body
    svg += f'    <circle r="7" fill="{CYAN}">\n'
    svg += f'      <animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto">\n'
    svg += f'        <mpath href="#snakePath"/>\n'
    svg += f'      </animateMotion>\n'
    svg += f'    </circle>\n'
    svg += f'  </g>\n'

    # ─── Glowing trail dots that fade behind the snake ───
    trail_count = 6
    for i in range(trail_count):
        delay = (i + 1) * 0.2
        r = 3 - i * 0.3
        op = 0.3 - i * 0.04
        svg += f'  <circle r="{r:.1f}" fill="{CYAN}" opacity="{op:.2f}">\n'
        svg += f'    <animateMotion dur="{dur}s" repeatCount="indefinite" begin="-{delay}s">\n'
        svg += f'      <mpath href="#snakePath"/>\n'
        svg += f'    </animateMotion>\n'
        svg += f'  </circle>\n'

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Snake animation → {output_path} ({total_points} path points, {dur:.1f}s loop)")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    generate_snake(username, os.path.join(assets, "snake.svg"))
