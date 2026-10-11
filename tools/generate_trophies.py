"""
Generate trophy SVG cards based on GitHub stats.
Trophies are awarded for various achievements with bronze/silver/gold/platinum tiers.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import (
    svg_header, svg_footer, text_el, format_number,
    PURPLE, CYAN, INDIGO, CARD_BG, BORDER, TEXT, TEXT_DIM,
    GREEN, ORANGE, RED
)
from github_client import compute_stats

# Trophy tiers and their colors
TIERS = {
    "bronze":   {"color": "#cd7f32", "label": "BRONZE",   "rank": 1},
    "silver":   {"color": "#c0c0c0", "label": "SILVER",   "rank": 2},
    "gold":     {"color": "#ffd700", "label": "GOLD",     "rank": 3},
    "platinum": {"color": "#e5e4e2", "label": "PLATINUM", "rank": 4},
}

# Trophy definitions: (key, label, icon_path_fn, thresholds)
# thresholds: [(count, tier), ...]  — last matching tier wins
_ICO = 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
TROPHY_DEFS = [
    ("stars", "Stars", lambda c: f'<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" {_ICO}/>',
     [(1, "bronze"), (10, "silver"), (50, "gold"), (200, "platinum")]),

    ("commits", "Commits", lambda c: f'<circle cx="12" cy="12" r="3.5" {_ICO}/><line x1="3" y1="12" x2="8.5" y2="12" stroke="currentColor" stroke-width="2"/><line x1="15.5" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>',
     [(10, "bronze"), (100, "silver"), (500, "gold"), (2000, "platinum")]),

    ("repos", "Repos", lambda c: f'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5z" {_ICO}/>',
     [(1, "bronze"), (5, "silver"), (15, "gold"), (50, "platinum")]),

    ("followers", "Followers", lambda c: f'<circle cx="9" cy="7" r="3.5" {_ICO}/><path d="M2.5 21v-2a4.5 4.5 0 0 1 4.5-4.5h4a4.5 4.5 0 0 1 4.5 4.5v2" {_ICO}/><path d="M16.5 4a3.5 3.5 0 0 1 0 7M21.5 21v-2a4.5 4.5 0 0 0-3-4.24" {_ICO} opacity="0.55"/>',
     [(1, "bronze"), (10, "silver"), (50, "gold"), (200, "platinum")]),

    ("forks", "Forks", lambda c: f'<circle cx="6" cy="6" r="2.6" {_ICO}/><circle cx="6" cy="18" r="2.6" {_ICO}/><circle cx="18" cy="6" r="2.6" {_ICO}/><line x1="6" y1="8.6" x2="6" y2="15.4" stroke="currentColor" stroke-width="2"/><path d="M18 8.6a9 9 0 0 1-9 9" {_ICO}/>',
     [(1, "bronze"), (5, "silver"), (20, "gold"), (100, "platinum")]),

    ("languages", "Languages", lambda c: f'<path d="M12 2L2 7l10 5 10-5-10-5z" {_ICO}/><path d="M2 17l10 5 10-5" {_ICO}/><path d="M2 12l10 5 10-5" {_ICO}/>',
     [(1, "bronze"), (3, "silver"), (6, "gold"), (10, "platinum")]),

    ("pull-requests", "Pull Requests", lambda c: f'<circle cx="18" cy="18" r="3" {_ICO}/><circle cx="6" cy="6" r="3" {_ICO}/><path d="M13 6h3a2 2 0 0 1 2 2v7" {_ICO}/><line x1="6" y1="9" x2="6" y2="21" stroke="currentColor" stroke-width="2"/>',
     [(1, "bronze"), (10, "silver"), (50, "gold"), (200, "platinum")]),

    ("issues", "Issues", lambda c: f'<circle cx="12" cy="12" r="9" {_ICO}/><circle cx="12" cy="12" r="3" fill="currentColor"/>',
     [(1, "bronze"), (10, "silver"), (50, "gold"), (200, "platinum")]),

    ("reviews", "Reviews", lambda c: f'<circle cx="12" cy="12" r="9" {_ICO}/><path d="M8 12l3 3 5-6" {_ICO}/>',
     [(1, "bronze"), (10, "silver"), (50, "gold"), (200, "platinum")]),
]


def _get_trophy_value(key, stats):
    """Get the metric value for a trophy key."""
    mapping = {
        "stars": stats["total_stars"],
        "commits": stats["total_commits"],
        "repos": stats["total_repos"],
        "followers": stats["followers"],
        "forks": stats["total_forks"],
        "languages": len(stats["languages"]),
        "pull-requests": stats.get("total_prs", 0),
        "issues": stats.get("total_issues", 0),
        "reviews": stats.get("total_reviews", 0),
    }
    return mapping.get(key, 0)


def _get_tier(value, thresholds):
    """Determine the trophy tier for a given value."""
    tier = None
    for threshold, t in thresholds:
        if value >= threshold:
            tier = t
    return tier


def _trophy_svg(x, y, w, h, label, tier_info, icon_fn, value):
    """Generate a single trophy card SVG fragment."""
    color = tier_info["color"]
    tier_label = tier_info["label"]

    svg = f'  <g transform="translate({x}, {y})">\n'
    # Card background
    svg += f'    <rect width="{w}" height="{h}" rx="10" fill="{CARD_BG}" stroke="{color}" stroke-width="1.5" opacity="0.95"/>\n'
    # Top accent bar
    svg += f'    <rect width="{w}" height="4" rx="2" fill="{color}"/>\n'
    # Trophy icon
    svg += f'    <g transform="translate({w // 2 - 12}, 14)" color="{color}">\n'
    svg += f'      <svg width="24" height="24" viewBox="0 0 24 24">{icon_fn(color)}</svg>\n'
    svg += f'    </g>\n'
    # Tier label
    svg += text_el(w // 2, 58, tier_label, font_size=10, fill=color,
                   weight="bold", anchor="middle")
    # Trophy name
    svg += text_el(w // 2, 75, label, font_size=11, fill=TEXT, anchor="middle")
    # Value
    svg += text_el(w // 2, 92, format_number(value), font_size=16,
                   fill=color, weight="bold", anchor="middle")

    svg += '  </g>\n'
    return svg


def generate_trophies(stats, output_path):
    """Generate the full trophies SVG."""
    # Determine which trophies are earned
    earned = []
    for key, label, icon_fn, thresholds in TROPHY_DEFS:
        value = _get_trophy_value(key, stats)
        tier = _get_tier(value, thresholds)
        if tier:
            earned.append((label, TIERS[tier], icon_fn, value))

    if not earned:
        # Show a placeholder
        earned = [("Get Started", TIERS["bronze"], lambda c: '<text x="12" y="16" text-anchor="middle" font-size="14" fill="currentColor">?</text>', 0)]

    # Layout: up to 7 trophies, arranged in rows
    trophy_w = 100
    trophy_h = 100
    gap = 10
    per_row = min(len(earned), 7)

    total_w = per_row * trophy_w + (per_row - 1) * gap + 20
    rows = (len(earned) + per_row - 1) // per_row
    total_h = rows * trophy_h + (rows - 1) * gap + 20

    svg = svg_header(total_w, total_h)
    svg += f'  <rect width="{total_w}" height="{total_h}" fill="none"/>\n'

    for i, (label, tier_info, icon_fn, value) in enumerate(earned):
        col = i % per_row
        row = i // per_row
        x = 10 + col * (trophy_w + gap)
        y = 10 + row * (trophy_h + gap)
        svg += _trophy_svg(x, y, trophy_w, trophy_h, label, tier_info, icon_fn, value)

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Trophies ({len(earned)} earned) → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    print(f"Fetching stats for trophies ({username})...")
    stats = compute_stats(username)
    generate_trophies(stats, os.path.join(assets, "trophies.svg"))
