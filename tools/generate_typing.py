"""
Generate an animated typing SVG using SMIL.
Uses a SINGLE global timeline — all phrases share the same dur and repeatCount.
Each phrase is only visible during its time slot via synchronized opacity + mask animations.
No overlapping, no drift.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, PURPLE, CYAN, DARK_BG, TEXT

WIDTH = 620
HEIGHT = 60
FONT_SIZE = 26
FONT_FAMILY = "Fira Code, Consolas, Courier New, monospace"
X_START = 10
Y_TEXT = 38


def _text_width(text, font_size=FONT_SIZE):
    """Estimate monospace text width."""
    return len(text) * font_size * 0.62


def generate_typing(phrases, output_path):
    """
    Generate a typing animation with a single global timeline.
    Each phrase: types in → holds → erases → pause before next.
    """
    # Calculate timing for each phrase
    phrase_timings = []
    current_time = 0.0

    for phrase in phrases:
        tw = _text_width(phrase)
        type_dur = max(len(phrase) * 0.08, 0.5)
        hold_dur = 1.5
        erase_dur = max(len(phrase) * 0.05, 0.3)
        pause_dur = 0.4

        phrase_timings.append({
            "text": phrase,
            "width": tw,
            "start": current_time,
            "type_end": current_time + type_dur,
            "hold_end": current_time + type_dur + hold_dur,
            "erase_end": current_time + type_dur + hold_dur + erase_dur,
            "end": current_time + type_dur + hold_dur + erase_dur + pause_dur,
        })
        current_time += type_dur + hold_dur + erase_dur + pause_dur

    total_dur = current_time

    svg = svg_header(WIDTH, HEIGHT)
    svg += f'  <rect width="{WIDTH}" height="{HEIGHT}" fill="none"/>\n'

    # ─── For each phrase: a mask (typing/erasing) + opacity (visibility) ───
    for i, pt in enumerate(phrase_timings):
        tw = pt["width"]
        s = pt["start"]
        te = pt["type_end"]
        he = pt["hold_end"]
        ee = pt["erase_end"]
        end = pt["end"]

        # ── Mask: controls the typing/erasing width ──
        # All masks use the SAME dur (total_dur) and begin="0s" — no drift
        mask_id = f"mask{i}"
        svg += f'  <mask id="{mask_id}">\n'
        svg += f'    <rect x="{X_START}" y="0" width="0" height="{HEIGHT}" fill="white">\n'

        # Build values and keyTimes for the ENTIRE timeline
        # Points: 0→start (width=0), start→type_end (0→tw), type_end→hold_end (tw),
        #         hold_end→erase_end (tw→0), erase_end→total_dur (0)
        mask_values = []
        mask_keytimes = []

        def add_point(t, w):
            mask_values.append(f"{w:.1f}")
            mask_keytimes.append(f"{t / total_dur:.6f}")

        add_point(0, 0)
        add_point(s, 0)
        add_point(te, tw)
        add_point(he, tw)
        add_point(ee, 0)
        add_point(total_dur, 0)

        svg += f'      <animate attributeName="width" dur="{total_dur:.2f}s" '
        svg += f'begin="0s" repeatCount="indefinite" '
        svg += f'values="{";".join(mask_values)}" '
        svg += f'keyTimes="{";".join(mask_keytimes)}"/>\n'
        svg += f'    </rect>\n'
        svg += f'  </mask>\n'

        # ── Text element with mask + opacity safety net ──
        # Opacity: 0 everywhere except during [start, erase_end]
        svg += f'  <text x="{X_START}" y="{Y_TEXT}" font-size="{FONT_SIZE}" '
        svg += f'font-family="{FONT_FAMILY}" font-weight="600" fill="{PURPLE}" '
        svg += f'mask="url(#{mask_id})" opacity="0">\n'
        svg += f'    {pt["text"]}\n'

        # Opacity animation on the same global timeline
        op_values = []
        op_keytimes = []

        def add_op(t, v):
            op_values.append(f"{v}")
            op_keytimes.append(f"{t / total_dur:.6f}")

        add_op(0, 0)
        add_op(s, 0)
        add_op(s + 0.01, 1)       # fade in instantly at start
        add_op(ee - 0.01, 1)      # stay visible until erase done
        add_op(ee, 0)             # fade out instantly at erase end
        add_op(total_dur, 0)

        svg += f'    <animate attributeName="opacity" dur="{total_dur:.2f}s" '
        svg += f'begin="0s" repeatCount="indefinite" '
        svg += f'values="{";".join(op_values)}" '
        svg += f'keyTimes="{";".join(op_keytimes)}"/>\n'
        svg += f'  </text>\n'

    # ─── Blinking cursor ───
    # The cursor x position follows the currently typing text
    cursor_values = []
    cursor_keytimes = []

    def add_cursor(t, x):
        cursor_values.append(f"{x:.1f}")
        cursor_keytimes.append(f"{t / total_dur:.6f}")

    add_cursor(0, X_START)

    for pt in phrase_timings:
        add_cursor(pt["start"], X_START)
        add_cursor(pt["type_end"], X_START + pt["width"])
        add_cursor(pt["hold_end"], X_START + pt["width"])
        add_cursor(pt["erase_end"], X_START)
        add_cursor(pt["end"], X_START)

    add_cursor(total_dur, X_START)

    cursor_y_top = Y_TEXT - FONT_SIZE + 4
    cursor_height = FONT_SIZE

    svg += f'  <rect x="{X_START}" y="{cursor_y_top}" width="3" height="{cursor_height}" '
    svg += f'fill="{CYAN}" rx="1">\n'
    svg += f'    <animate attributeName="x" dur="{total_dur:.2f}s" '
    svg += f'begin="0s" repeatCount="indefinite" '
    svg += f'values="{";".join(cursor_values)}" '
    svg += f'keyTimes="{";".join(cursor_keytimes)}"/>\n'
    # Blink
    svg += f'    <animate attributeName="opacity" dur="0.8s" '
    svg += f'repeatCount="indefinite" values="1;1;0;0;1" '
    svg += f'keyTimes="0;0.45;0.5;0.95;1"/>\n'
    svg += f'  </rect>\n'

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Typing animation ({len(phrases)} phrases, {total_dur:.1f}s loop) → {output_path}")


if __name__ == "__main__":
    assets = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets, exist_ok=True)
    phrases = sys.argv[1:] if len(sys.argv) > 1 else [
        "Cybersecurity Student",
        "CTF Toolbox Developer",
        "Full-Stack Developer",
        "Python | TypeScript | Rust",
    ]
    generate_typing(phrases, os.path.join(assets, "typing.svg"))
