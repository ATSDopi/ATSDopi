"""
Generate an animated snake SVG that moves across the contribution grid.
The snake follows a path through the grid cells, eating contributions.
Uses SMIL <animateMotion> for the snake animation.
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
        # Generate empty grid
        grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
    else:
        # Build the grid: 7 rows (days of week) x 52 cols (weeks)
        sorted_days = sorted(days, key=lambda d: d["date"])

        # Find the start date (Sunday of the first week)
        if sorted_days:
            first = datetime.strptime(sorted_days[0]["date"], "%Y-%m-%d")
            start_date = first - timedelta(days=first.weekday() + 1)
            if start_date.weekday() == 6:  # Sunday
                start_date = first
        else:
            start_date = datetime.now() - timedelta(days=364)

        # Build date→count map
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

    # Generate a snake path through the grid
    # The snake moves left-to-right, weaving up and down
    path_points = []
    for col in range(GRID_COLS):
        if col % 2 == 0:
            # Go top to bottom
            for row in range(GRID_ROWS):
                cx = offset_x + col * CELL_SIZE + CELL / 2
                cy = offset_y + row * CELL_SIZE + CELL / 2
                path_points.append((cx, cy))
        else:
            # Go bottom to top
            for row in range(GRID_ROWS - 1, -1, -1):
                cx = offset_x + col * CELL_SIZE + CELL / 2
                cy = offset_y + row * CELL_SIZE + CELL / 2
                path_points.append((cx, cy))

    # Build the motion path
    path_d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in path_points)

    # Calculate total path length for animation timing
    total_points = len(path_points)
    # Duration scales with grid size
    dur = max(total_points * 0.08, 10)

    # Define the snake path (invisible, used for animateMotion)
    svg += f'  <path id="snakePath" d="{path_d}" fill="none" stroke="none"/>\n'

    # Snake body — a series of circles that follow the path with delays
    # We use animateMotion with keyPoints to create a trailing effect
    snake_segments = 8
    seg_radius = 5

    for i in range(snake_segments):
        # Each segment starts at a different point along the path
        # Segment 0 is the head (front), later segments trail behind
        offset = i / snake_segments
        begin_delay = i * 0.15

        svg += f'  <circle r="{seg_radius - i * 0.3:.1f}" fill="{PURPLE if i == 0 else INDIGO}" opacity="{1 - i * 0.08:.2f}" filter="url(#glow)">\n'
        svg += f'    <animateMotion dur="{dur}s" repeatCount="indefinite" begin="-{begin_delay}s">\n'
        svg += f'      <mpath href="#snakePath"/>\n'
        svg += f'    </animateMotion>\n'
        svg += f'  </circle>\n'

    # Snake head with eyes (follows the path first)
    svg += f'  <g filter="url(#glow)">\n'
    svg += f'    <circle r="6" fill="{CYAN}">\n'
    svg += f'      <animateMotion dur="{dur}s" repeatCount="indefinite">\n'
    svg += f'        <mpath href="#snakePath"/>\n'
    svg += f'      </animateMotion>\n'
    svg += f'    </circle>\n'
    # Eyes (small white dots that move with the head)
    svg += f'    <circle r="1.5" fill="white">\n'
    svg += f'      <animateMotion dur="{dur}s" repeatCount="indefinite" begin="0s">\n'
    svg += f'        <mpath href="#snakePath"/>\n'
    svg += f'      </animateMotion>\n'
    svg += f'    </circle>\n'
    svg += f'  </g>\n'

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Snake animation → {output_path} ({total_points} path points, {dur:.1f}s loop)")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    generate_snake(username, os.path.join(assets, "snake.svg"))
