"""
Generate a streak stats card SVG from contribution calendar data.
Calculates current streak, longest streak, and total contributions.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import (
    svg_header, svg_footer, card_bg, text_el, format_number,
    PURPLE, CYAN, INDIGO, CARD_BG, BORDER, TEXT, TEXT_DIM, GREEN, ORANGE
)
from github_client import get_contributions

W, H = 460, 195


def _compute_streaks(days):
    """
    Compute current and longest streaks from contribution days.
    A streak is consecutive days with >= 1 contribution.
    """
    if not days:
        return {"current": 0, "longest": 0, "total": 0, "today": 0}

    # Sort days by date
    sorted_days = sorted(days, key=lambda d: d["date"])

    # Get today and yesterday
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    total = sum(d["contributionCount"] for d in sorted_days)

    # Compute longest streak
    longest = 0
    current_run = 0
    for d in sorted_days:
        if d["contributionCount"] > 0:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 0

    # Compute current streak (counting back from today or yesterday)
    current = 0
    # Build a date→count map
    date_map = {d["date"]: d["contributionCount"] for d in sorted_days}

    # Start from today; if today has 0, start from yesterday (streak not broken yet today)
    check_date = today
    if date_map.get(today, 0) == 0:
        check_date = yesterday

    while True:
        count = date_map.get(check_date, 0)
        if count > 0:
            current += 1
            d = datetime.strptime(check_date, "%Y-%m-%d")
            check_date = (d - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            break

    today_count = date_map.get(today, 0)

    return {
        "current": current,
        "longest": longest,
        "total": total,
        "today": today_count,
    }


def _flame_icon(cx, cy, color):
    """Draw a simple flame icon."""
    return f'''  <g transform="translate({cx}, {cy})">
    <path d="M7 0C5 3 3 5 3 9c0 4 3 7 7 7s7-3 7-7c0-2-1-4-2-5c0 1-1 2-2 2c0-3-2-5-4-6c0 2-1 3-2 3c0-3-1-5-2-3z" fill="{color}" filter="url(#glow)"/>
  </g>'''


def generate_streak(username, output_path):
    """Generate the streak card SVG."""
    print(f"  Fetching contributions for {username}...")
    contribs = get_contributions(username)
    streak = _compute_streaks(contribs["days"])

    svg = svg_header(W, H)
    svg += card_bg(W, H)

    # Title
    svg += text_el(W // 2, 32, "🔥 Streak Stats", font_size=16,
                   fill=ORANGE, weight="bold", anchor="middle")
    svg += f'  <rect x="{W // 2 - 90}" y="40" width="180" height="2" rx="1" fill="url(#gradHeader)" opacity="0.6"/>\n'

    # Three big numbers: Current, Longest, Total
    col_w = W // 3

    # Current streak
    cx = col_w // 2
    svg += _flame_icon(cx - 8, 60, ORANGE if streak["current"] > 0 else TEXT_DIM)
    svg += text_el(cx, 110, str(streak["current"]), font_size=36,
                   fill=ORANGE, weight="bold", anchor="middle")
    svg += text_el(cx, 130, "Current", font_size=12,
                   fill=TEXT_DIM, anchor="middle")
    svg += text_el(cx, 148, "Days", font_size=11,
                   fill=TEXT_DIM, anchor="middle")

    # Longest streak
    cx = col_w + col_w // 2
    svg += text_el(cx, 95, str(streak["longest"]), font_size=36,
                   fill=PURPLE, weight="bold", anchor="middle")
    svg += text_el(cx, 115, "Longest", font_size=12,
                   fill=TEXT_DIM, anchor="middle")
    svg += text_el(cx, 133, "Streak", font_size=11,
                   fill=TEXT_DIM, anchor="middle")

    # Total contributions
    cx = 2 * col_w + col_w // 2
    svg += text_el(cx, 95, format_number(streak["total"]), font_size=36,
                   fill=CYAN, weight="bold", anchor="middle")
    svg += text_el(cx, 115, "Total", font_size=12,
                   fill=TEXT_DIM, anchor="middle")
    svg += text_el(cx, 133, "Contributions", font_size=11,
                   fill=TEXT_DIM, anchor="middle")

    # Divider lines
    svg += f'  <line x1="{col_w}" y1="60" x2="{col_w}" y2="155" stroke="{BORDER}" stroke-width="1" opacity="0.5"/>\n'
    svg += f'  <line x1="{2 * col_w}" y1="60" x2="{2 * col_w}" y2="155" stroke="{BORDER}" stroke-width="1" opacity="0.5"/>\n'

    # Today's contributions
    today_label = "Today"
    svg += text_el(W // 2, H - 15,
                   f"{today_label}: {streak['today']} contribution{'s' if streak['today'] != 1 else ''}",
                   font_size=12, fill=GREEN if streak["today"] > 0 else TEXT_DIM,
                   anchor="middle")

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Streak card → {output_path} (current={streak['current']}, longest={streak['longest']}, total={streak['total']})")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    generate_streak(username, os.path.join(assets, "streak.svg"))
