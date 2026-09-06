"""
Generate a contribution calendar heatmap SVG.
Shows when commits happened over the last year — like GitHub's contribution graph.
Each cell is a day, colored by contribution count.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import (
    svg_header, svg_footer, card_bg, text_el,
    PURPLE, CYAN, INDIGO, CARD_BG, BORDER, TEXT, TEXT_DIM
)
from github_client import get_contributions

CELL = 13
CELL_GAP = 3
CELL_SIZE = CELL + CELL_GAP
GRID_COLS = 53  # weeks (full year)
GRID_ROWS = 7   # days of week


def _level_color(count):
    """Map contribution count to a color level (GitHub-style green scale)."""
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


def _level_label(count):
    if count == 0:
        return "No"
    elif count <= 3:
        return "Low"
    elif count <= 6:
        return "Mid"
    elif count <= 9:
        return "High"
    else:
        return "Max"


def generate_contributions(username, output_path):
    """Generate the contribution calendar heatmap SVG."""
    print(f"  Fetching contributions for heatmap ({username})...")
    contribs = get_contributions(username)
    days = contribs["days"]

    # Layout
    label_w = 30  # space for day-of-week labels on left
    title_h = 50
    legend_h = 30
    grid_w = GRID_COLS * CELL_SIZE
    grid_h = GRID_ROWS * CELL_SIZE
    W = grid_w + label_w + 30
    H = grid_h + title_h + legend_h + 20

    svg = svg_header(W, H)
    svg += card_bg(W, H)

    # Title
    svg += text_el(20, 30, f"Commit Activity — Last Year",
                   font_size=16, fill=PURPLE, weight="bold")
    svg += f'  <rect x="20" y="38" width="220" height="2" rx="1" fill="url(#gradHeader)" opacity="0.6"/>\n'

    # Build the grid
    if not days:
        grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
    else:
        sorted_days = sorted(days, key=lambda d: d["date"])
        first = datetime.strptime(sorted_days[0]["date"], "%Y-%m-%d")
        # Align to Sunday (start of week)
        start_date = first - timedelta(days=first.weekday() + 1)
        if start_date.weekday() == 6:
            start_date = first

        date_map = {d["date"]: d["contributionCount"] for d in sorted_days}
        grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                d = start_date + timedelta(days=col * 7 + row)
                key = d.strftime("%Y-%m-%d")
                grid[row][col] = date_map.get(key, 0)

    # Day-of-week labels (Mon, Wed, Fri)
    day_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    offset_x = label_w + 10
    offset_y = title_h + 5

    for row_idx, label in day_labels.items():
        y = offset_y + row_idx * CELL_SIZE + CELL / 2 + 4
        svg += text_el(15, y, label, font_size=10, fill=TEXT_DIM, anchor="start")

    # Month labels along the top
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    last_month = -1
    for col in range(GRID_COLS):
        # Check what month this column starts in
        if days:
            sorted_days_d = sorted(days, key=lambda d: d["date"])
            first_d = datetime.strptime(sorted_days_d[0]["date"], "%Y-%m-%d")
            sd = first_d - timedelta(days=first_d.weekday() + 1)
            if sd.weekday() == 6:
                sd = first_d
            d = sd + timedelta(days=col * 7)
            m = d.month - 1
        else:
            m = col // 5  # fallback
        if m != last_month and col < GRID_COLS:
            x = offset_x + col * CELL_SIZE
            svg += text_el(x, offset_y - 8, month_names[m % 12],
                           font_size=10, fill=TEXT_DIM, anchor="start")
            last_month = m

    # Draw the contribution cells
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            count = grid[row][col]
            color = _level_color(count)
            x = offset_x + col * CELL_SIZE
            y = offset_y + row * CELL_SIZE
            svg += f'  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>\n'

    # Legend (bottom right)
    legend_y = offset_y + grid_h + 15
    legend_x = W - 200

    svg += text_el(legend_x - 10, legend_y + 10, "Less",
                   font_size=10, fill=TEXT_DIM, anchor="end")

    levels = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    for i, color in enumerate(levels):
        lx = legend_x + i * (CELL + 2)
        svg += f'  <rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>\n'

    svg += text_el(legend_x + len(levels) * (CELL + 2) + 8, legend_y + 10,
                   "More", font_size=10, fill=TEXT_DIM, anchor="start")

    # Summary stats
    total = sum(grid[row][col] for row in range(GRID_ROWS) for col in range(GRID_COLS))
    active_days = sum(1 for row in range(GRID_ROWS) for col in range(GRID_COLS) if grid[row][col] > 0)
    svg += text_el(20, legend_y + 10,
                   f"{total} contributions in the last year",
                   font_size=11, fill=TEXT, weight="bold")
    svg += text_el(20, legend_y + 25,
                   f"{active_days} active days",
                   font_size=10, fill=TEXT_DIM)

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Contribution heatmap → {output_path} ({total} contributions, {active_days} active days)")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    generate_contributions(username, os.path.join(assets, "snake.svg"))
