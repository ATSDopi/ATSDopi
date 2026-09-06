"""
Generate an animated typing SVG using SMIL.
Single global timeline — all phrases share the same dur and begin.
Text is CENTERED horizontally. No overlapping, no drift.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from svg_utils import svg_header, svg_footer, PURPLE, CYAN, DARK_BG, TEXT

WIDTH = 620
HEIGHT = 60
FONT_SIZE = 26
FONT_FAMILY = "Fira Code, Consolas, Courier New, monospace"
CENTER_X = WIDTH // 2
Y_TEXT = 38


def _text_width(text, font_size=FONT_SIZE):
    """Estimate monospace text width."""
    return len(text) * font_size * 0.62


def generate_typing(phrases, output_path):
    """
    Generate a CENTERED typing animation with a single global timeline.
    Each phrase: types in → holds → erases → pause before next.
    The mask grows from the CENTER outward so text appears centered.
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

    for i, pt in enumerate(phrase_timings):
        tw = pt["width"]
        s = pt["start"]
        te = pt["type_end"]
        he = pt["hold_end"]
        ee = pt["erase_end"]

        # Centered mask: rect grows from center outward
        # x starts at CENTER_X (width=0) and moves left as width grows
        # x = CENTER_X - width/2, width = current_width
        mask_id = f"mask{i}"
        svg += f'  <mask id="{mask_id}">\n'
        svg += f'    <rect x="{CENTER_X}" y="0" width="0" height="{HEIGHT}" fill="white">\n'

        mask_values = []
        mask_keytimes = []

        def add_point(t, w):
            # x = CENTER_X - w/2, width = w
            mask_values.append(f"{CENTER_X - w / 2:.1f};{w:.1f}")
            mask_keytimes.append(f"{t / total_dur:.6f}")

        add_point(0, 0)
        add_point(s, 0)
        add_point(te, tw)
        add_point(he, tw)
        add_point(ee, 0)
        add_point(total_dur, 0)

        svg += f'      <animate attributeName="x" dur="{total_dur:.2f}s" '
        svg += f'begin="0s" repeatCount="indefinite" '
        svg += f'values="{";".join(v.split(";")[0] for v in mask_values)}" '
        svg += f'keyTimes="{";".join(mask_keytimes)}"/>\n'
        svg += f'      <animate attributeName="width" dur="{total_dur:.2f}s" '
        svg += f'begin="0s" repeatCount="indefinite" '
        svg += f'values="{";".join(v.split(";")[1] for v in mask_values)}" '
        svg += f'keyTimes="{";".join(mask_keytimes)}"/>\n'
        svg += f'    </rect>\n'
        svg += f'  </mask>\n'

        # Text element — CENTERED with text-anchor="middle"
        svg += f'  <text x="{CENTER_X}" y="{Y_TEXT}" font-size="{FONT_SIZE}" '
        svg += f'font-family="{FONT_FAMILY}" font-weight="600" fill="{PURPLE}" '
        svg += f'text-anchor="middle" mask="url(#{mask_id})" opacity="0">\n'
        svg += f'    {pt["text"]}\n'

        # Opacity safety net
        op_values = []
        op_keytimes = []

        def add_op(t, v):
            op_values.append(f"{v}")
            op_keytimes.append(f"{t / total_dur:.6f}")

        add_op(0, 0)
        add_op(s, 0)
        add_op(s + 0.01, 1)
        add_op(ee - 0.01, 1)
        add_op(ee, 0)
        add_op(total_dur, 0)

        svg += f'    <animate attributeName="opacity" dur="{total_dur:.2f}s" '
        svg += f'begin="0s" repeatCount="indefinite" '
        svg += f'values="{";".join(op_values)}" '
        svg += f'keyTimes="{";".join(op_keytimes)}"/>\n'
        svg += f'  </text>\n'

    # ─── Blinking cursor — centered ───
    cursor_values = []
    cursor_keytimes = []

    def add_cursor(t, x):
        cursor_values.append(f"{x:.1f}")
        cursor_keytimes.append(f"{t / total_dur:.6f}")

    add_cursor(0, CENTER_X)

    for pt in phrase_timings:
        # Cursor starts at center, moves right as text types
        add_cursor(pt["start"], CENTER_X - pt["width"] / 2)
        add_cursor(pt["type_end"], CENTER_X + pt["width"] / 2)
        add_cursor(pt["hold_end"], CENTER_X + pt["width"] / 2)
        add_cursor(pt["erase_end"], CENTER_X - pt["width"] / 2)
        add_cursor(pt["end"], CENTER_X)

    add_cursor(total_dur, CENTER_X)

    cursor_y_top = Y_TEXT - FONT_SIZE + 4
    cursor_height = FONT_SIZE

    svg += f'  <rect x="{CENTER_X}" y="{cursor_y_top}" width="3" height="{cursor_height}" '
    svg += f'fill="{CYAN}" rx="1">\n'
    svg += f'    <animate attributeName="x" dur="{total_dur:.2f}s" '
    svg += f'begin="0s" repeatCount="indefinite" '
    svg += f'values="{";".join(cursor_values)}" '
    svg += f'keyTimes="{";".join(cursor_keytimes)}"/>\n'
    svg += f'    <animate attributeName="opacity" dur="0.8s" '
    svg += f'repeatCount="indefinite" values="1;1;0;0;1" '
    svg += f'keyTimes="0;0.45;0.5;0.95;1"/>\n'
    svg += f'  </rect>\n'

    svg += svg_footer()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✓ Typing animation ({len(phrases)} phrases, {total_dur:.1f}s loop, centered) → {output_path}")


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
