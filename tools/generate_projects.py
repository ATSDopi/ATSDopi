"""
Generate featured project cards — one standalone SVG per repository.
Data comes from the user's real pinned repos (GraphQL pinnedItems),
padded with top-starred public repos when fewer than `count` are pinned.

Each card is written to its own file (project-0.svg ... project-N.svg) so the
README can wrap each <img> in an <a> — making every card clickable.
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import (
    svg_header, svg_footer, card_bg, text_el, xml_escape,
    PURPLE, CYAN, INDIGO, CARD_BG, BORDER, TEXT, TEXT_DIM, GREEN
)
from github_client import get_pinned_repos

CARD_W = 445
CARD_H = 118
NUM_CARDS = 4

# Max chars per description line (445px card, ~7px/char at 12px)
DESC_CHARS = 62


def _wrap(text, width, max_lines=2):
    """Naive word-wrap into at most `max_lines` lines of `width` chars."""
    if not text:
        return []
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:width - 1].rstrip() + "…"
    return lines


def _repo_icon():
    return (f'<path d="M4 3a2 2 0 00-2 2v14a2 2 0 002 2h16a2 2 0 002-2V7a2 2 0 00-2-2h-7l-2-2H4z" '
            f'fill="none" stroke="{CYAN}" stroke-width="1.8"/>')


def _star_icon():
    return f'<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="{CYAN}"/>'


def _fork_icon():
    return (f'<circle cx="6" cy="6" r="2.4" fill="{INDIGO}"/><circle cx="18" cy="6" r="2.4" fill="{INDIGO}"/>'
            f'<circle cx="12" cy="18" r="2.4" fill="{INDIGO}"/>'
            f'<path d="M6 8.5V12h12V8.5M12 12v3.5" stroke="{INDIGO}" stroke-width="1.8" fill="none"/>')


def _card(repo):
    """Render one project card."""
    name = repo["name"]
    desc = repo.get("description") or "No description yet — work in progress."
    # Strip leading emoji — they render as flat monochrome glyphs inside SVG text
    desc = re.sub(r"^[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\s]+", "", desc).strip()
    lang = repo.get("primaryLanguage") or {}
    lang_name = lang.get("name")
    lang_color = lang.get("color") or INDIGO
    stars = repo.get("stargazerCount", 0)
    forks = repo.get("forkCount", 0)

    svg = svg_header(CARD_W, CARD_H)
    svg += card_bg(CARD_W, CARD_H, rx=10)

    # Top accent line (gradient)
    svg += f'  <rect width="{CARD_W}" height="3" rx="1.5" fill="url(#gradHeader)" opacity="0.8"/>\n'

    # Repo icon + name
    svg += f'  <g transform="translate(18, 16)"><svg width="18" height="18" viewBox="0 0 24 24">{_repo_icon()}</svg></g>\n'
    display_name = name if len(name) <= 40 else name[:38] + "…"
    svg += text_el(44, 30, xml_escape(display_name), font_size=15,
                   fill=CYAN, weight="bold")

    # Description (up to 2 wrapped lines)
    desc_lines = _wrap(desc, DESC_CHARS)
    has_desc = bool(repo.get("description"))
    y = 54
    for line in desc_lines:
        svg += text_el(18, y, xml_escape(line), font_size=12,
                       fill=TEXT_DIM if has_desc else TEXT_DIM,
                       opacity=1 if has_desc else 0.6)
        y += 16

    # Bottom meta row: language dot, stars, forks
    meta_y = CARD_H - 14
    x = 18
    if lang_name:
        svg += f'  <circle cx="{x + 5}" cy="{meta_y - 4}" r="5" fill="{lang_color}"/>\n'
        svg += text_el(x + 16, meta_y, xml_escape(lang_name), font_size=11, fill=TEXT)
        x += 16 + len(lang_name) * 7 + 18
    svg += f'  <g transform="translate({x}, {meta_y - 12})"><svg width="13" height="13" viewBox="0 0 24 24">{_star_icon()}</svg></g>\n'
    svg += text_el(x + 16, meta_y, str(stars), font_size=11, fill=TEXT_DIM)
    x += 16 + len(str(stars)) * 7 + 16
    svg += f'  <g transform="translate({x}, {meta_y - 12})"><svg width="13" height="13" viewBox="0 0 24 24">{_fork_icon()}</svg></g>\n'
    svg += text_el(x + 16, meta_y, str(forks), font_size=11, fill=TEXT_DIM)

    svg += svg_footer()
    return svg


def generate_projects(username, assets_dir, count=NUM_CARDS):
    """
    Generate `count` project card SVGs: project-0.svg … project-N.svg.
    Also writes assets/projects-fragment.html — the matching <a><img> snippet
    (SVGs inside <img> can't carry links, so the README wraps each card).
    """
    repos = get_pinned_repos(username, count)
    paths = []
    links = []
    for i, repo in enumerate(repos):
        path = os.path.join(assets_dir, f"project-{i}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(_card(repo))
        paths.append((path, repo))
        links.append(f'  <a href="{repo["url"]}"><img src="./assets/project-{i}.svg" width="{CARD_W}" alt="{repo["name"]}" /></a>')
        print(f"  ✓ {repo['name']:24s} → assets/project-{i}.svg")

    fragment = os.path.join(assets_dir, "projects-fragment.html")
    with open(fragment, "w", encoding="utf-8") as f:
        f.write("\n".join(links) + "\n")
    return paths


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    username = sys.argv[1] if len(sys.argv) > 1 else "ATSDopi"
    generate_projects(username, assets)
