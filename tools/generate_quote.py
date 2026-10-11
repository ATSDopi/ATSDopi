"""
Generate a "quote of the day" SVG strip.
Rotates daily through a curated list of security/dev quotes — the card
changes every day even when nothing else does. No API needed.
"""

import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import (
    svg_header, svg_footer, text_el, xml_escape,
    PURPLE, CYAN, TEXT_DIM, CARD_BG, BORDER
)

W = 620
H = 74

QUOTES = [
    ("The quieter you become, the more you can hear.", "Ram Dass — Kali Linux motto"),
    ("Hack the planet.", "Hackers (1995)"),
    ("It's not a bug, it's an undocumented feature.", "Every developer ever"),
    ("Security is a process, not a product.", "Bruce Schneier"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("With great power comes great responsibility.", "Uncle Ben — and every root shell"),
    ("There are only two types of companies: those that have been hacked, and those that will be.", "Robert Mueller"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("Stay hungry, stay foolish.", "Steve Jobs"),
    ("Amateurs hack systems, professionals hack people.", "Bruce Schneier"),
    ("Simplicity is the soul of efficiency.", "Austin Freeman"),
    ("The shell is mightier than the sword.", "Unknown"),
    ("Trust, but verify.", "Zero-trust proverb"),
    ("Every system is perfectly designed to get the result it does.", "W. Edwards Deming"),
    ("Move fast and break things — then document the breakage.", "Dev proverb"),
    ("Offense for fun, defense for a living.", "Security proverb"),
    ("If you can't measure it, you can't secure it.", "Security proverb"),
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
]


def _wrap(text, width=64):
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
    return lines[:2]


def generate_quote(output_path):
    """Generate the daily quote strip."""
    day_idx = datetime.now(timezone.utc).timetuple().tm_yday
    quote, author = QUOTES[day_idx % len(QUOTES)]

    svg = svg_header(W, H)
    svg += f'  <rect width="{W}" height="{H}" rx="10" fill="{CARD_BG}" stroke="{BORDER}" stroke-width="1"/>\n'
    svg += f'  <rect width="4" height="{H - 16}" x="8" y="8" rx="2" fill="url(#gradHeader)"/>\n'

    # Big decorative quote mark
    svg += text_el(26, 42, "“", font_size=40, fill=PURPLE, weight="bold", opacity=0.8)

    lines = _wrap(quote)
    if len(lines) == 1:
        svg += (f'  <text x="58" y="34" font-size="13" font-style="italic" '
                f'font-family="Georgia, serif" fill="#c9d1d9">{xml_escape(lines[0])}</text>\n')
        svg += text_el(58, 58, f"— {xml_escape(author)}", font_size=11, fill=TEXT_DIM)
    else:
        svg += (f'  <text x="58" y="26" font-size="13" font-style="italic" '
                f'font-family="Georgia, serif" fill="#c9d1d9">{xml_escape(lines[0])}</text>\n')
        svg += (f'  <text x="58" y="44" font-size="13" font-style="italic" '
                f'font-family="Georgia, serif" fill="#c9d1d9">{xml_escape(lines[1])}</text>\n')
        svg += text_el(58, 62, f"— {xml_escape(author)}", font_size=11, fill=TEXT_DIM)

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Quote of the day (day {day_idx}) → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    generate_quote(os.path.join(assets, "quote.svg"))
