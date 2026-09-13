from __future__ import annotations

from pathlib import Path

from hotwire_core.models import Airfoil, Point2D


class DatFormatError(ValueError):
    """when cant convert dat to airfoil"""


def _parse_pair(line: str) -> tuple[float, float] | None:
    parts = line.replace(",", " ").split()
    if len(parts) != 2:
        return None
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        return None


def load_dat(path: Path | str) -> Airfoil:
    path = Path(path)
    lines = [line.strip() for line in path.read_text().splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        raise DatFormatError(f"{path.name}: file is empty")

    name = path.stem
    rows: list[tuple[float, float]] = []
    for index, line in enumerate(lines):
        pair = _parse_pair(line)
        if pair is None:
            if index == 0:
                name = line
                continue
            raise DatFormatError(f"{path.name}: unparseable  {index + 1}: {line!r}")
        rows.append(pair)

    if rows and rows[0][0] > 1.0 and rows[0][1] > 1.0:
        rows = _lednicer_to_selig(rows)

    if not rows:
        return Airfoil(name=name, points=[])

    points = [Point2D(x, y) for x, y in _drop_adjacent_duplicates(rows)]
    return Airfoil(name=name, points=points)


def _lednicer_to_selig(rows: list[tuple[float, float]]) -> list[tuple[float, float]]:
    upper_count = int(round(rows[0][0]))
    lower_count = int(round(rows[0][1]))
    coords = rows[1:]
    upper = coords[:upper_count]
    lower = coords[upper_count : upper_count + lower_count]
    if len(lower) > 1:
        return list(reversed(upper)) + lower[1:]
    return list(reversed(upper)) + lower


def _drop_adjacent_duplicates(rows: list[tuple[float, float]]) -> list[tuple[float, float]]:
    result = [rows[0]]
    for row in rows[1:]:
        if row != result[-1]:
            result.append(row)
    return result
