"""
Generate an activity graph SVG from contribution calendar data.
Shows a line/area chart of daily contributions over the last ~30 days.
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

W = 900
H = 320
PADDING_L = 60
PADDING_R = 30
PADDING_T = 50
PADDING_B = 50
CHART_W = W - PADDING_L - PADDING_R
CHART_H = H - PADDING_T - PADDING_B


def generate_activity_graph(username, output_path):
    """Generate the activity graph SVG."""
    print(f"  Fetching contributions for activity graph ({username})...")
    contribs = get_contributions(username)
    days = contribs["days"]

    if not days:
        # Empty state
        svg = svg_header(W, H)
        svg += card_bg(W, H)
        svg += text_el(W // 2, H // 2, "No contribution data available",
                       font_size=16, fill=TEXT_DIM, anchor="middle")
        svg += svg_footer()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)
        return

    # Sort by date and take last 30 days
    sorted_days = sorted(days, key=lambda d: d["date"])
    recent = sorted_days[-30:]

    values = [d["contributionCount"] for d in recent]
    max_val = max(values) if values else 1
    max_val = max(max_val, 5)  # Minimum scale of 5

    svg = svg_header(W, H)
    svg += card_bg(W, H)

    # Title
    svg += text_el(20, 32, f"📈 Activity — Last {len(recent)} Days",
                   font_size=16, fill=PURPLE, weight="bold")
    svg += f'  <rect x="20" y="40" width="250" height="2" rx="1" fill="url(#gradHeader)" opacity="0.6"/>\n'

    # Y-axis grid lines and labels
    grid_steps = 5
    for i in range(grid_steps + 1):
        val = (max_val / grid_steps) * (grid_steps - i)
        y = PADDING_T + (CHART_H / grid_steps) * i
        svg += f'  <line x1="{PADDING_L}" y1="{y:.0f}" x2="{W - PADDING_R}" y2="{y:.0f}" stroke="{BORDER}" stroke-width="0.5" opacity="0.3"/>\n'
        svg += text_el(PADDING_L - 8, y + 4, f"{int(val)}",
                       font_size=10, fill=TEXT_DIM, anchor="end")

    # X-axis labels (every 5 days)
    for i, day in enumerate(recent):
        if i % 5 == 0 or i == len(recent) - 1:
            x = PADDING_L + (CHART_W / (len(recent) - 1)) * i
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            label = date_obj.strftime("%b %d")
            svg += text_el(x, H - PADDING_B + 20, label,
                           font_size=10, fill=TEXT_DIM, anchor="middle")

    # Area path
    points = []
    for i, val in enumerate(values):
        x = PADDING_L + (CHART_W / (len(values) - 1)) * i
        y = PADDING_T + CHART_H - (val / max_val) * CHART_H
        points.append((x, y))

    # Area fill
    area_path = f"M{PADDING_L},{PADDING_T + CHART_H} "
    area_path += " ".join(f"L{x:.1f},{y:.1f}" for x, y in points)
    area_path += f" L{PADDING_L + CHART_W},{PADDING_T + CHART_H} Z"

    svg += f'  <path d="{area_path}" fill="url(#gradPurple)" opacity="0.3"/>\n'

    # Line path
    line_path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    svg += f'  <path d="{line_path}" fill="none" stroke="{CYAN}" stroke-width="2" filter="url(#glow)"/>\n'

    # Data points
    for i, (x, y) in enumerate(points):
        if values[i] > 0:
            svg += f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{PURPLE}" stroke="{CYAN}" stroke-width="1"/>\n'

    # Stats summary
    total = sum(values)
    avg = total / len(values) if values else 0
    max_day = max(values) if values else 0

    svg += text_el(W - PADDING_R, H - 15,
                   f"Total: {total}  •  Avg: {avg:.1f}/day  •  Max: {max_day}",
                   font_size=11, fill=TEXT_DIM, anchor="end")

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Activity graph → {output_path} (total={total}, avg={avg:.1f}, max={max_day})")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    generate_activity_graph(username, os.path.join(assets, "activity-graph.svg"))
