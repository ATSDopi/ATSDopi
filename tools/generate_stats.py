"""
Generate GitHub stats card and top-languages card as SVG.
Fetches real data from the GitHub API and renders polished SVG cards
with the dark-neon theme.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import (
    svg_header, svg_footer, card_bg, text_el, format_number, xml_escape,
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
    return (f'<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" '
            f'fill="none" stroke="{CYAN}" stroke-width="2" stroke-linejoin="round"/>')


def _icon_contributions():
    # activity pulse
    return (f'<polyline points="22 12 18 12 15 21 9 3 6 12 2 12" fill="none" '
            f'stroke="{PURPLE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')


def _icon_commits():
    # git-commit: center dot on a line
    return (f'<circle cx="12" cy="12" r="3.5" fill="none" stroke="{PURPLE}" stroke-width="2"/>'
            f'<line x1="3" y1="12" x2="8.5" y2="12" stroke="{PURPLE}" stroke-width="2"/>'
            f'<line x1="15.5" y1="12" x2="21" y2="12" stroke="{PURPLE}" stroke-width="2"/>')


def _icon_fork():
    # git-branch style
    return (f'<circle cx="6" cy="6" r="2.6" fill="none" stroke="{INDIGO}" stroke-width="2"/>'
            f'<circle cx="6" cy="18" r="2.6" fill="none" stroke="{INDIGO}" stroke-width="2"/>'
            f'<circle cx="18" cy="6" r="2.6" fill="none" stroke="{INDIGO}" stroke-width="2"/>'
            f'<line x1="6" y1="8.6" x2="6" y2="15.4" stroke="{INDIGO}" stroke-width="2"/>'
            f'<path d="M18 8.6a9 9 0 0 1-9 9" fill="none" stroke="{INDIGO}" stroke-width="2"/>')


def _icon_repo():
    # book icon
    return (f'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5z" '
            f'fill="none" stroke="{GREEN}" stroke-width="2" stroke-linejoin="round"/>')


def _icon_followers():
    # users icon
    return (f'<circle cx="9" cy="7" r="3.5" fill="none" stroke="{CYAN}" stroke-width="2"/>'
            f'<path d="M2.5 21v-2a4.5 4.5 0 0 1 4.5-4.5h4a4.5 4.5 0 0 1 4.5 4.5v2" fill="none" stroke="{CYAN}" stroke-width="2"/>'
            f'<path d="M16.5 4a3.5 3.5 0 0 1 0 7" fill="none" stroke="{CYAN}" stroke-width="2" opacity="0.55"/>'
            f'<path d="M21.5 21v-2a4.5 4.5 0 0 0-3-4.24" fill="none" stroke="{CYAN}" stroke-width="2" opacity="0.55"/>')


def _stat_row(svg, x, y, icon_svg, label, value, w):
    """Add a stat row with icon, label, and value. Numbers right-aligned."""
    svg += f'  <g transform="translate({x}, {y})">\n'
    svg += f'    <svg width="24" height="24" viewBox="0 0 24 24">{icon_svg}</svg>\n'
    svg += text_el(32, 17, label, font_size=13, fill=TEXT_DIM)
    # Right-align all values at the same x position (with padding from border)
    svg += text_el(w - 45, 17, value, font_size=14, fill=TEXT, weight="bold", anchor="end")
    svg += '  </g>\n'
    return svg


def generate_stats_card(stats, output_path):
    """Generate the main stats card SVG."""
    svg = svg_header(STATS_W, STATS_H)
    svg += card_bg(STATS_W, STATS_H)

    # Title
    svg += text_el(20, 32, f"{xml_escape(stats['username'])}'s GitHub Stats",
                   font_size=16, fill=PURPLE, weight="bold")
    # Underline
    svg += f'  <rect x="20" y="40" width="180" height="2" rx="1" fill="url(#gradHeader)" opacity="0.6"/>\n'

    # Stats rows — real per-type counters from GraphQL (last year window)
    rows = [
        (_icon_contributions(), "Contributions (1y)", format_number(stats["total_contributions"])),
        (_icon_commits(), "Commits (1y)", format_number(stats["total_commits"])),
        (_icon_star(), "Total Stars", format_number(stats["total_stars"])),
        (_icon_fork(), "Total Forks", format_number(stats["total_forks"])),
        (_icon_repo(), "Public Repos", format_number(stats["total_repos"])),
        (_icon_followers(), "Followers", format_number(stats["followers"])),
    ]

    y = 56
    for icon, label, value in rows:
        svg = _stat_row(svg, 20, y, icon, label, value, STATS_W)
        y += 23

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Stats card → {output_path}")


def _arc(cx, cy, r_out, r_in, a0, a1):
    """Donut segment path between two angles (degrees, 0 = top)."""
    import math
    p0o = (cx + r_out * math.sin(math.radians(a0)), cy - r_out * math.cos(math.radians(a0)))
    p1o = (cx + r_out * math.sin(math.radians(a1)), cy - r_out * math.cos(math.radians(a1)))
    p1i = (cx + r_in * math.sin(math.radians(a1)), cy - r_in * math.cos(math.radians(a1)))
    p0i = (cx + r_in * math.sin(math.radians(a0)), cy - r_in * math.cos(math.radians(a0)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f'M{p0o[0]:.2f} {p0o[1]:.2f} '
            f'A{r_out} {r_out} 0 {large} 1 {p1o[0]:.2f} {p1o[1]:.2f} '
            f'L{p1i[0]:.2f} {p1i[1]:.2f} '
            f'A{r_in} {r_in} 0 {large} 0 {p0i[0]:.2f} {p0i[1]:.2f} Z')


def generate_top_langs(stats, output_path):
    """Generate the top-languages card as a donut chart of real byte shares."""
    svg = svg_header(LANGS_W, LANGS_H)
    svg += card_bg(LANGS_W, LANGS_H)

    # Title
    svg += text_el(20, 32, "Most Used Languages",
                   font_size=16, fill=PURPLE, weight="bold")
    svg += f'  <rect x="20" y="40" width="200" height="2" rx="1" fill="url(#gradHeader)" opacity="0.6"/>\n'

    # Real byte shares per language (fallback: repo counts)
    sizes = stats.get("lang_bytes") or stats.get("languages") or {}
    langs = sorted(sizes.items(), key=lambda x: x[1], reverse=True)
    total = sum(v for _, v in langs) or 1

    top = langs[:6]
    if len(langs) > 6:
        top.append(("Other", sum(v for _, v in langs[6:])))

    # Donut — left side
    cx, cy, r_out, r_in = 112, 126, 54, 34
    angle = 0.0
    for lang, size in top:
        frac = size / total
        if frac >= 0.9999:
            color = LANG_COLORS.get(lang, INDIGO)
            svg += f'  <circle cx="{cx}" cy="{cy}" r="{(r_out + r_in) / 2}" fill="none" stroke="{color}" stroke-width="{r_out - r_in}"/>\n'
        else:
            sweep = frac * 360
            color = LANG_COLORS.get(lang, INDIGO)
            svg += f'  <path d="{_arc(cx, cy, r_out, r_in, angle, angle + sweep)}" fill="{color}" stroke="{CARD_BG}" stroke-width="1.5"/>\n'
            angle += sweep

    # Center label: dominant language share
    if top:
        name, size = top[0]
        svg += text_el(cx, cy - 2, f"{size / total * 100:.0f}%",
                       font_size=20, fill=TEXT, weight="bold", anchor="middle")
        label = name if len(name) <= 12 else name[:11] + "…"
        svg += text_el(cx, cy + 15, xml_escape(label),
                       font_size=10, fill=TEXT_DIM, anchor="middle")

    # Legend — right side, two columns if needed
    lx = 195
    y = 78
    for lang, size in top:
        color = LANG_COLORS.get(lang, INDIGO)
        pct = size / total * 100
        svg += f'  <circle cx="{lx + 6}" cy="{y - 4}" r="5" fill="{color}"/>\n'
        name = lang if len(lang) <= 14 else lang[:13] + "…"
        svg += text_el(lx + 18, y, xml_escape(name), font_size=12, fill=TEXT)
        svg += text_el(LANGS_W - 24, y, f"{pct:.1f}%",
                       font_size=12, fill=TEXT_DIM, weight="bold", anchor="end")
        y += 19

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
