"""Schematic figure for the paper (v1.1): how the two series of 25b-28b are laid.

A small 9 x 9 grid stands in for the 49 x 49 one; it holds no letters from the edition.
(a) series A, the "black" squares (row + column even), written along diagonals down to the
right (the `/` letters); (b) series B, the "white" squares, written up to the left (the `~`
letters of 25b and 26a); (c) the line lengths of each colour set out as rows, centred, the shape
of the partly filled tables of 29a-48b. Usage: weave_figure.py -> paper/weave-schema.svg
"""

from loag import ROOT

N = 9
S = 22  # cell size
GAP = 46
DARK, LIGHT, EDGE = "#5b6f8f", "#e6dcc3", "#333333"
ARROW_A, ARROW_B = "#b03a2e", "#1f5f8b"


def grid(x0, y0, lit):
    out = []
    for r in range(N):
        for c in range(N):
            colour = DARK if (r + c) % 2 == 0 else LIGHT
            op = "1" if (r + c) % 2 == lit else "0.35"
            out.append(f'<rect x="{x0 + c * S}" y="{y0 + r * S}" width="{S}" height="{S}" '
                       f'fill="{colour}" fill-opacity="{op}" stroke="#999" stroke-width="0.4"/>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{N * S}" height="{N * S}" fill="none" '
               f'stroke="{EDGE}" stroke-width="1"/>')
    return out


def diagonals(x0, y0, par, step, colour, marker):
    """One arrow per line: the cells of one colour along a diagonal, in the writing direction."""
    out = []
    dr = step[0]
    for k in range(-(N - 1), N):  # r - c = k on a (+1, +1) diagonal
        if (k % 2) != par:
            continue
        cells = [(r, r - k) for r in range(N) if 0 <= r - k < N]
        if dr < 0:
            cells = cells[::-1]
        (r0, c0), (r1, c1) = cells[0], cells[-1]
        x_0, y_0 = x0 + c0 * S + S / 2, y0 + r0 * S + S / 2
        x_1, y_1 = x0 + c1 * S + S / 2, y0 + r1 * S + S / 2
        if len(cells) == 1:
            out.append(f'<circle cx="{x_0}" cy="{y_0}" r="2.6" fill="{colour}"/>')
            continue
        out.append(f'<line x1="{x_0}" y1="{y_0}" x2="{x_1}" y2="{y_1}" '
                   f'stroke="{colour}" stroke-width="1.6" marker-end="url(#{marker})"/>')
    return out


def diamond(x0, y0, lengths, colour, label_dy):
    out = []
    w = max(lengths)
    for i, n in enumerate(lengths):
        xs = x0 + (w - n) * S * 0.5 / 2
        for j in range(n):
            out.append(f'<rect x="{xs + j * S * 0.5}" y="{y0 + i * S * 0.5}" '
                       f'width="{S * 0.5 - 1}" height="{S * 0.5 - 1}" fill="{colour}"/>')
        out.append(f'<text x="{x0 + w * S * 0.5 + 6}" y="{y0 + i * S * 0.5 + label_dy}" '
                   f'font-size="10" fill="#444">{n}</text>')
    return out


def main():
    a = [2 * i + 1 for i in range(N // 2 + 1)] + [2 * i + 1 for i in range(N // 2 - 1, -1, -1)]
    b = [2 * i for i in range(1, N // 2 + 1)] + [2 * i for i in range(N // 2, 0, -1)]
    W = 3 * N * S + 2 * GAP + 70
    H = N * S + 40 + 8
    top = 30
    x1, x2, x3 = 10, 10 + N * S + GAP, 10 + 2 * (N * S + GAP)
    body = ['<defs>']
    for name, col in (("ha", ARROW_A), ("hb", ARROW_B)):
        body.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" '
                    f'markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
                    f'fill="{col}"/></marker>')
    body.append('</defs>')
    body += grid(x1, top, 0) + diagonals(x1, top, 0, (1, 1), ARROW_A, "ha")
    body += grid(x2, top, 1) + diagonals(x2, top, 1, (-1, -1), ARROW_B, "hb")
    body += diamond(x3, top, a, DARK, 9)
    body += diamond(x3 + 5.5 * S, top + 0.5 * S, b, "#b9a77a", 9)
    for x, t in ((x1, "(a) series A: dark squares, down-right"),
                 (x2, "(b) series B: light squares, up-left"),
                 (x3, "(c) the lines set out as rows")):
        body.append(f'<text x="{x}" y="16" font-size="12" fill="#222">{t}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="sans-serif">\n<rect width="{W}" height="{H}" '
           f'fill="white"/>\n' + "\n".join(body) + "\n</svg>\n")
    (ROOT / "paper" / "weave-schema.svg").write_text(svg)


if __name__ == "__main__":
    main()
