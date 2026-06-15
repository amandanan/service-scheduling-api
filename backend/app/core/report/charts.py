"""Tiny SVG chart builders for the PDF report.

The charts are intentionally simple (a handful of bars or points), so building
the SVG by hand keeps us dependency-free and on-brand. WeasyPrint rasterises
inline SVG crisply, so these strings drop straight into the HTML template.
"""

from xml.sax.saxutils import escape

PURPLE = "#6d28d9"
PURPLE_LIGHT = "#c4b5fd"
INK = "#1f2937"
GRID = "#e5e7eb"
MUTED = "#9ca3af"


def _money(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def _truncate(text: str, limit: int = 18) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def empty_chart(message: str = "Sem dados no período", width: int = 540, height: int = 80) -> str:
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" '
        f'dominant-baseline="middle" fill="{MUTED}" font-size="13" '
        f'font-family="Helvetica, Arial, sans-serif">{escape(message)}</text></svg>'
    )


def horizontal_bars(
    items,
    label_key,
    value_key,
    money=True,
    width=540,
    row_h=30,
    label_w=140,
    value_w=80,
) -> str:
    """Horizontal bar chart: a labelled row per item, bar length proportional
    to the value, with the formatted value at the end."""

    if not items:
        return empty_chart()

    max_value = max(float(it[value_key]) for it in items) or 1.0
    bar_max = width - label_w - value_w
    height = row_h * len(items) + 8

    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Helvetica, Arial, sans-serif">'
    ]

    for i, it in enumerate(items):
        value = float(it[value_key])
        y = i * row_h + 4
        bar_w = max((value / max_value) * bar_max, 2)
        cy = y + row_h / 2
        label = _truncate(str(it[label_key]))
        shown = _money(value) if money else f"{value:g}"

        parts.append(
            f'<text x="0" y="{cy}" dominant-baseline="middle" fill="{INK}" '
            f'font-size="12.5">{escape(label)}</text>'
        )
        parts.append(
            f'<rect x="{label_w}" y="{y + 5}" width="{bar_max}" '
            f'height="{row_h - 14}" rx="4" fill="{GRID}"/>'
        )
        parts.append(
            f'<rect x="{label_w}" y="{y + 5}" width="{bar_w:.1f}" '
            f'height="{row_h - 14}" rx="4" fill="{PURPLE}"/>'
        )
        parts.append(
            f'<text x="{width}" y="{cy}" text-anchor="end" '
            f'dominant-baseline="middle" fill="{INK}" font-size="12.5" '
            f'font-weight="700">{escape(shown)}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def vertical_bars(items, label_key, value_key, width=540, height=220) -> str:
    """Vertical bar chart (e.g. appointments per weekday)."""

    if not items:
        return empty_chart()

    pad_bottom = 28
    pad_top = 16
    plot_h = height - pad_bottom - pad_top
    max_value = max(int(it[value_key]) for it in items) or 1
    slot = width / len(items)
    bar_w = slot * 0.55

    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Helvetica, Arial, sans-serif">'
    ]
    # baseline
    parts.append(
        f'<line x1="0" y1="{pad_top + plot_h}" x2="{width}" '
        f'y2="{pad_top + plot_h}" stroke="{GRID}"/>'
    )

    for i, it in enumerate(items):
        value = int(it[value_key])
        bar_h = (value / max_value) * plot_h
        x = i * slot + (slot - bar_w) / 2
        y = pad_top + plot_h - bar_h
        cx = i * slot + slot / 2

        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" '
            f'height="{bar_h:.1f}" rx="4" fill="{PURPLE}"/>'
        )
        if value:
            parts.append(
                f'<text x="{cx:.1f}" y="{y - 4:.1f}" text-anchor="middle" '
                f'fill="{INK}" font-size="11" font-weight="700">{value}</text>'
            )
        parts.append(
            f'<text x="{cx:.1f}" y="{height - 8}" text-anchor="middle" '
            f'fill="{MUTED}" font-size="11">{escape(str(it[label_key]))}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def line_chart(items, label_key, value_key, width=540, height=200) -> str:
    """Line chart (e.g. revenue over the last months)."""

    if not items:
        return empty_chart()

    pad = {"left": 8, "right": 8, "top": 18, "bottom": 26}
    plot_w = width - pad["left"] - pad["right"]
    plot_h = height - pad["top"] - pad["bottom"]
    max_value = max(float(it[value_key]) for it in items) or 1.0

    n = len(items)
    step = plot_w / (n - 1) if n > 1 else 0

    points = []
    for i, it in enumerate(items):
        value = float(it[value_key])
        x = pad["left"] + i * step
        y = pad["top"] + plot_h - (value / max_value) * plot_h
        points.append((x, y, it[label_key], value))

    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in points)

    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Helvetica, Arial, sans-serif">'
    ]
    parts.append(
        f'<line x1="{pad["left"]}" y1="{pad["top"] + plot_h}" '
        f'x2="{width - pad["right"]}" y2="{pad["top"] + plot_h}" stroke="{GRID}"/>'
    )
    parts.append(
        f'<polyline fill="none" stroke="{PURPLE}" stroke-width="2.5" '
        f'points="{poly}"/>'
    )
    for x, y, label, _ in points:
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{PURPLE}"/>')
        parts.append(
            f'<text x="{x:.1f}" y="{height - 8}" text-anchor="middle" '
            f'fill="{MUTED}" font-size="11">{escape(str(label))}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)
