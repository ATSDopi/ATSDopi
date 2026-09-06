"""
Shared SVG utility helpers.
Provides color palette, font definitions, gradient defs,
card backgrounds, and common SVG building blocks.
"""

# ─── Color Palette (Dark Neon Theme) ───
PURPLE = "#a333d8"
CYAN = "#00d4ff"
INDIGO = "#7287fd"
DARK_BG = "#0d1117"
CARD_BG = "#161b22"
BORDER = "#30363d"
TEXT = "#c9d1d9"
TEXT_DIM = "#8b949e"
GREEN = "#39d353"
ORANGE = "#d29922"
RED = "#f85149"

# Gradient stops
GRADIENT_HEADER = [(0, INDIGO), (50, PURPLE), (100, CYAN)]
GRADIENT_FOOTER = [(0, CYAN), (50, PURPLE), (100, INDIGO)]


def svg_header(width, height, extra_defs=""):
    """Return the opening SVG tag with defs (gradients, filters, styles)."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
<defs>
  <linearGradient id="gradHeader" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="{INDIGO}"/>
    <stop offset="50%" stop-color="{PURPLE}"/>
    <stop offset="100%" stop-color="{CYAN}"/>
  </linearGradient>
  <linearGradient id="gradFooter" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="{CYAN}"/>
    <stop offset="50%" stop-color="{PURPLE}"/>
    <stop offset="100%" stop-color="{INDIGO}"/>
  </linearGradient>
  <linearGradient id="gradPurple" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="{PURPLE}" stop-opacity="0.8"/>
    <stop offset="100%" stop-color="{INDIGO}" stop-opacity="0.4"/>
  </linearGradient>
  <linearGradient id="gradCyan" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0.8"/>
    <stop offset="100%" stop-color="{PURPLE}" stop-opacity="0.4"/>
  </linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
    <feMerge>
      <feMergeNode in="coloredBlur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <filter id="glowStrong" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
    <feMerge>
      <feMergeNode in="coloredBlur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
{extra_defs}
</defs>
'''


def svg_footer():
    return "</svg>\n"


def card_bg(width, height, rx=12, fill=CARD_BG, stroke=BORDER):
    """Rounded rectangle card background."""
    return f'  <rect width="{width}" height="{height}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>\n'


def text_el(x, y, content, font_size=14, fill=TEXT, weight="normal",
            family="Segoe UI, Helvetica, Arial, sans-serif", anchor="start",
             opacity=1, filter_id=None):
    """Generate a <text> element."""
    filt = f' filter="url(#{filter_id})"' if filter_id else ""
    return (f'  <text x="{x}" y="{y}" font-size="{font_size}" '
            f'font-family="{family}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" opacity="{opacity}"{filt}>'
            f'{content}</text>\n')


def wrap_cdata(svg_content):
    """Wrap SVG content (not needed for <img> rendering, but keeps it clean)."""
    return svg_content


def format_number(n):
    """Format large numbers: 1.2k, 3.4M, etc."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)
