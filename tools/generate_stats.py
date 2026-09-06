"""
Generate GitHub stats card and top-languages card as SVG.
Fetches real data from the GitHub API and renders polished SVG cards
with the dark-neon theme.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import (
    svg_header, svg_footer, card_bg, text_el, format_number,
    PURPLE, CYAN, INDIGO, DARK_BG, CARD_BG, BORDER, TEXT, TEXT_DIM, GREEN
)
from github_client import compute_stats

STATS_W, STATS_H = 460, 195
LANGS_W, LANGS_H = 460, 195

# Language → color mapping (GitHub-style)
LANG_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "Dockerfile": "#384d54",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Java": "#b07219",
    "C": "#555555",
    "C++": "#f34b7d",
    "C#": "#178600",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "Vue": "#41b883",
    "Jupyter Notebook": "#DA5B0B",
}


def _icon_star():
    return f'<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="{CYAN}"/>'


def _icon_commits():
    return f'<circle cx="12" cy="12" r="3" fill="{PURPLE}"/><line x1="12" y1="2" x2="12" y2="9" stroke="{PURPLE}" stroke-width="2"/><line x1="12" y1="15" x2="12" y2="22" stroke="{PURPLE}" stroke-width="2"/><line x1="2" y1="12" x2="9" y2="12" stroke="{PURPLE}" stroke-width="2"/><line x1="15" y1="12" x2="22" y2="12" stroke="{PURPLE}" stroke-width="2"/>'


def _icon_fork():
    return f'<circle cx="6" cy="6" r="2.5" fill="{INDIGO}"/><circle cx="18" cy="6" r="2.5" fill="{INDIGO}"/><circle cx="12" cy="18" r="2.5" fill="{INDIGO}"/><line x1="6" y1="8.5" x2="6" y2="12" stroke="{INDIGO}" stroke-width="2"/><line x1="18" y1="8.5" x2="18" y2="12" stroke="{INDIGO}" stroke-width="2"/><line x1="6" y1="12" x2="18" y2="12" stroke="{INDIGO}" stroke-width="2"/><line x1="12" y1="12" x2="12" y2="15.5" stroke="{INDIGO}" stroke-width="2"/>'


def _icon_repo():
    return f'<path d="M4 2a2 2 0 00-2 2v16a2 2 0 002 2h16a2 2 0 002-2V4a2 2 0 00-2-2H4zm0 2h16v16H4V4zm2 2h6v2H6V6zm0 4h6v2H6v-2zm0 4h4v2H6v-2z" fill="{GREEN}"/>'


def _icon_followers():
    return f'<circle cx="9" cy="8" r="4" fill="{CYAN}"/><path d="M2 20c0-3.87 3.13-7 7-7s7 3.13 7 7" stroke="{CYAN}" stroke-width="2" fill="none"/><circle cx="17" cy="7" r="3" fill="{PURPLE}" opacity="0.6"/>'


def _stat_row(svg, x, y, icon_svg, label, value, w):
    """Add a stat row with icon, label, and value."""
    svg += f'  <g transform="translate({x}, {y})">\n'
    svg += f'    <svg width="24" height="24" viewBox="0 0 24 24">{icon_svg}</svg>\n'
    svg += text_el(32, 17, label, font_size=13, fill=TEXT_DIM)
    svg += text_el(w - 20, 17, value, font_size=14, fill=TEXT, weight="bold", anchor="end")
    svg += '  </g>\n'
    return svg


def generate_stats_card(stats, output_path):
    """Generate the main stats card SVG."""
    svg = svg_header(STATS_W, STATS_H)
    svg += card_bg(STATS_W, STATS_H)

    # Title
    svg += text_el(20, 32, f"{stats['username']}'s GitHub Stats",
                   font_size=16, fill=PURPLE, weight="bold")
    # Underline
    svg += f'  <rect x="20" y="40" width="180" height="2" rx="1" fill="url(#gradHeader)" opacity="0.6"/>\n'

    # Stats rows
    rows = [
        (_icon_repo(), "Total Repos", format_number(stats["total_repos"])),
        (_icon_commits(), "Total Commits", format_number(stats["total_commits"])),
        (_icon_star(), "Total Stars", format_number(stats["total_stars"])),
        (_icon_fork(), "Total Forks", format_number(stats["total_forks"])),
        (_icon_followers(), "Followers", format_number(stats["followers"])),
    ]

    y = 60
    for icon, label, value in rows:
        svg = _stat_row(svg, 20, y, icon, label, value, STATS_W)
        y += 27

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Stats card → {output_path}")


def generate_top_langs(stats, output_path):
    """Generate the top-languages card SVG with a horizontal bar chart."""
    svg = svg_header(LANGS_W, LANGS_H)
    svg += card_bg(LANGS_W, LANGS_H)

    # Title
    svg += text_el(20, 32, "Most Used Languages",
                   font_size=16, fill=PURPLE, weight="bold")
    svg += f'  <rect x="20" y="40" width="200" height="2" rx="1" fill="url(#gradHeader)" opacity="0.6"/>\n'

    # Sort languages by count
    langs = sorted(stats["languages"].items(), key=lambda x: x[1], reverse=True)
    total = sum(c for _, c in langs) or 1

    # Take top 5
    top = langs[:5]

    # Stacked bar
    bar_x = 20
    bar_y = 55
    bar_w = LANGS_W - 40
    bar_h = 10

    offset = bar_x
    for lang, count in top:
        color = LANG_COLORS.get(lang, INDIGO)
        w = (count / total) * bar_w
        svg += f'  <rect x="{offset:.1f}" y="{bar_y}" width="{w:.1f}" height="{bar_h}" rx="2" fill="{color}"/>\n'
        offset += w

    # Language list with percentages
    y = 85
    for lang, count in top:
        color = LANG_COLORS.get(lang, INDIGO)
        pct = (count / total) * 100
        # Color dot
        svg += f'  <circle cx="26" cy="{y - 4}" r="5" fill="{color}"/>\n'
        # Language name
        svg += text_el(38, y, lang, font_size=13, fill=TEXT)
        # Percentage
        svg += text_el(LANGS_W - 20, y, f"{pct:.1f}%",
                       font_size=13, fill=TEXT_DIM, anchor="end")
        y += 22

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Top languages → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    print(f"Fetching GitHub stats for {username}...")
    stats = compute_stats(username)
    generate_stats_card(stats, os.path.join(assets, "stats.svg"))
    generate_top_langs(stats, os.path.join(assets, "top-langs.svg"))
