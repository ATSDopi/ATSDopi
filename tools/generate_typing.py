"""
Generate an animated typing SVG using SMIL.
Simulates a typewriter effect by revealing text left-to-right with a mask,
cycling through multiple phrases with a blinking cursor.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, PURPLE, CYAN, DARK_BG, TEXT

WIDTH = 620
HEIGHT = 60
FONT_SIZE = 26
FONT_FAMILY = "Fira Code, Consolas, Courier New, monospace"


def _text_width(text, font_size=FONT_SIZE):
    """Estimate monospace text width."""
    return len(text) * font_size * 0.62


def generate_typing(phrases, output_path):
    """
    Generate a typing animation SVG.
    Each phrase is revealed character by character, held, then erased.
    """
    svg = svg_header(WIDTH, HEIGHT)

    svg += f'  <rect width="{WIDTH}" height="{HEIGHT}" fill="none"/>\n'

    # Mask that reveals text from left to right (typing effect)
    # We use a rect whose width animates to simulate typing
    svg += '  <mask id="typeMask">\n'
    svg += f'    <rect x="0" y="0" width="0" height="{HEIGHT}" fill="white" id="maskRect">\n'

    # Calculate timing for each phrase
    # Each phrase: type (len*0.08s) + hold (1s) + erase (len*0.05s) + pause (0.3s)
    total_time = 0
    mask_values = []  # list of (time, width)
    cursor_x_values = []  # list of (time, x)

    for phrase in phrases:
        tw = _text_width(phrase)
        type_dur = max(len(phrase) * 0.08, 0.5)
        hold_dur = 1.5
        erase_dur = max(len(phrase) * 0.05, 0.3)
        pause_dur = 0.4

        # Type: width goes 0 → tw
        mask_values.append((total_time, 0))
        mask_values.append((total_time + type_dur, tw))
        cursor_x_values.append((total_time, 0))
        cursor_x_values.append((total_time + type_dur, tw))

        # Hold: width stays at tw
        total_time += type_dur
        mask_values.append((total_time, tw))
        cursor_x_values.append((total_time, tw))

        # Hold
        total_time += hold_dur
        mask_values.append((total_time, tw))
        cursor_x_values.append((total_time, tw))

        # Erase: width goes tw → 0
        mask_values.append((total_time + erase_dur, 0))
        cursor_x_values.append((total_time + erase_dur, 0))

        total_time += erase_dur + pause_dur
        mask_values.append((total_time, 0))
        cursor_x_values.append((total_time, 0))

    # Build mask animation values string
    mask_val_str = ";".join(f"{w}" for _, w in mask_values)
    mask_time_str = ";".join(f"{t:.2f}s" for t, _ in mask_values)

    svg += f'      <animate attributeName="width" dur="{total_time:.1f}s" '
    svg += f'repeatCount="indefinite" values="{mask_val_str}" '
    svg += f'keyTimes="{";".join(f"{t/total_time:.4f}" for t, _ in mask_values)}"/>\n'
    svg += '    </rect>\n'
    svg += '  </mask>\n'

    # Build the text content — all phrases overlaid, each visible during its time slot
    x_start = 10
    y_text = HEIGHT // 2 + FONT_SIZE // 3

    for idx, phrase in enumerate(phrases):
        tw = _text_width(phrase)
        type_dur = max(len(phrase) * 0.08, 0.5)
        hold_dur = 1.5
        erase_dur = max(len(phrase) * 0.05, 0.3)
        pause_dur = 0.4

        # Calculate this phrase's start time
        start_t = 0
        for prev in phrases[:idx]:
            start_t += max(len(prev) * 0.08, 0.5) + 1.5 + max(len(prev) * 0.05, 0.3) + 0.4

        phrase_dur = type_dur + hold_dur + erase_dur

        # Individual mask for this phrase
        mask_id = f"phraseMask{idx}"
        svg += f'  <mask id="{mask_id}">\n'
        svg += f'    <rect x="{x_start}" y="0" width="0" height="{HEIGHT}" fill="white" id="maskRect{idx}">\n'

        # Type phase
        p_mask_values = []
        t = 0
        p_mask_values.append((t, 0))
        t += type_dur
        p_mask_values.append((t, tw))
        t += hold_dur
        p_mask_values.append((t, tw))
        t += erase_dur
        p_mask_values.append((t, 0))

        p_val_str = ";".join(f"{w}" for _, w in p_mask_values)
        p_keytimes = ";".join(f"{t_val / phrase_dur:.4f}" for t_val, _ in p_mask_values)

        svg += f'      <animate attributeName="width" dur="{phrase_dur:.2f}s" '
        svg += f'begin="{start_t:.2f}s" repeatCount="indefinite" '
        svg += f'values="{p_val_str}" keyTimes="{p_keytimes}"/>\n'
        svg += '    </rect>\n'
        svg += '  </mask>\n'

        # The text element, masked
        svg += f'  <text x="{x_start}" y="{y_text}" font-size="{FONT_SIZE}" '
        svg += f'font-family="{FONT_FAMILY}" font-weight="600" fill="{PURPLE}" '
        svg += f'mask="url(#{mask_id})">{phrase}</text>\n'

    # Blinking cursor — appears at the end of typed text
    # We animate its x position and opacity
    cursor_x = x_start
    cursor_y_top = y_text - FONT_SIZE + 4
    cursor_y_bot = y_text + 4

    # Build cursor x animation
    cursor_times = []
    cursor_xs = []
    t = 0
    for phrase in phrases:
        tw = _text_width(phrase)
        type_dur = max(len(phrase) * 0.08, 0.5)
        hold_dur = 1.5
        erase_dur = max(len(phrase) * 0.05, 0.3)
        pause_dur = 0.4

        cursor_times.append(t)
        cursor_xs.append(x_start)
        t += type_dur
        cursor_times.append(t)
        cursor_xs.append(x_start + tw)
        t += hold_dur
        cursor_times.append(t)
        cursor_xs.append(x_start + tw)
        t += erase_dur
        cursor_times.append(t)
        cursor_xs.append(x_start)
        t += pause_dur

    cursor_keytimes = ";".join(f"{t_val / total_time:.4f}" for t_val in cursor_times)
    cursor_x_vals = ";".join(f"{x}" for x in cursor_xs)

    svg += f'  <rect x="{x_start}" y="{cursor_y_top}" width="3" height="{FONT_SIZE}" '
    svg += f'fill="{CYAN}" rx="1" id="cursor">\n'
    svg += f'    <animate attributeName="x" dur="{total_time:.1f}s" '
    svg += f'repeatCount="indefinite" values="{cursor_x_vals}" '
    svg += f'keyTimes="{cursor_keytimes}"/>\n'
    # Blink
    svg += f'    <animate attributeName="opacity" dur="0.8s" '
    svg += f'repeatCount="indefinite" values="1;1;0;0;1" '
    svg += f'keyTimes="0;0.45;0.5;0.95;1"/>\n'
    svg += '  </rect>\n'

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Typing animation → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    phrases = sys.argv[1:] if len(sys.argv) > 1 else [
        "Full-Stack Developer",
        "Backend Engineer",
        "Cybersecurity Enthusiast",
        "Python | TypeScript | HTML",
    ]
    generate_typing(phrases, os.path.join(assets, "typing.svg"))
