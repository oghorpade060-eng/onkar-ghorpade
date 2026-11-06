"""Synthetic campus-library analytics using only the Python standard library."""
import argparse
import csv
import html
import json
import random
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
AS_OF = "2026-11-01"
QUERIES = ["overview", "category_demand", "monthly_activity", "category_ranking", "overdue_loans", "inventory"]
BOOKS = [
    (1, "Python Lab Notes", "Programming", 5), (2, "SQL in Practice", "Programming", 5),
    (3, "Java Fundamentals", "Programming", 4), (4, "Data Structures", "Programming", 4),
    (5, "Probability Workbook", "Mathematics", 4), (6, "Linear Algebra Notes", "Mathematics", 4),
    (7, "Statistics Through Examples", "Mathematics", 4), (8, "Machine Learning Lab", "AI & Data", 6),
    (9, "Working with Data", "AI & Data", 5), (10, "Neural Network Notes", "AI & Data", 3),
    (11, "Linux Lab", "Systems", 3), (12, "Networks Workbook", "Systems", 3),
]


def database():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript((ROOT / "sql" / "schema.sql").read_text())
    return connection


def seed(connection):
    rng = random.Random(42)
    connection.executemany("INSERT INTO books VALUES (?, ?, ?, ?)", BOOKS)
    departments = ["AI & DS", "Computer", "Mechanical", "Electronics"]
    connection.executemany("INSERT INTO members VALUES (?, ?)",
                           [(f"M{i:03}", departments[(i - 1) % 4]) for i in range(1, 49)])
    loans = []
    start, end = date(2026, 5, 1), date.fromisoformat(AS_OF)
    for offset in range((end - start).days):
        day = start + timedelta(days=offset)
        for _ in range(rng.randint(1, 4)):
            book = rng.choice(BOOKS)
            occupied = sum(row[1] == book[0] and (row[5] is None or row[5] > day.isoformat()) for row in loans)
            if occupied >= book[3]:
                continue
            due = day + timedelta(days=14)
            returned = day + timedelta(days=rng.randint(5, 26))
            returned_value = returned.isoformat() if returned < end else None
            loans.append((len(loans) + 1, book[0], f"M{rng.randint(1, 48):03}",
                          day.isoformat(), due.isoformat(), returned_value))
    connection.executemany("INSERT INTO loans VALUES (?, ?, ?, ?, ?, ?)", loans)
    connection.commit()


def query_cursor(connection, name, as_of=AS_OF):
    if name not in QUERIES:
        raise ValueError("Unknown report.")
    # Bound parameters also prevent a date string from becoming executable SQL.
    return connection.execute((ROOT / "sql" / f"{name}.sql").read_text(), {"as_of": as_of})


def run_query(connection, name, as_of=AS_OF):
    return [dict(row) for row in query_cursor(connection, name, as_of)]


def validate_date(value):
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Use an ISO date, YYYY-MM-DD.") from error
    if parsed.isoformat() != value or not date(2026, 5, 1) <= parsed <= date.fromisoformat(AS_OF):
        raise ValueError(f"Use a date from 2026-05-01 through {AS_OF}.")
    return value


def render_html(report):
    def table(rows):
        if not rows:
            return '<p class="note">No matching rows.</p>'
        head = ''.join(f'<th>{html.escape(key.replace("_", " "))}</th>' for key in rows[0])
        body = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(value)) if value is not None else "—"}</td>' for value in row.values()) + '</tr>' for row in rows)
        return f'<div class="table-scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
    summary = report["queries"]["overview"][0]
    cards = ''.join(f'<div class="metric"><span>{key.replace("_", " ")}</span><strong>{value}</strong></div>' for key, value in summary.items())
    category_rows = report["queries"]["category_demand"]
    maximum = max((row["loans"] for row in category_rows), default=1) or 1
    bars = ''.join(f'<div class="bar-row"><span>{html.escape(row["category"])}</span><div class="track"><div style="width:{100 * row["loans"] / maximum:.2f}%"></div></div><strong>{row["loans"]}</strong></div>' for row in category_rows)
    sections = ''
    for name, rows in report["queries"].items():
        if name == "overview":
            continue
        note = '<p class="note">The final month may be incomplete. These are raw monthly counts; a partial-month drop is not a measured trend.</p>' if name == "monthly_activity" else ''
        sections += f'<section><h2>{name.replace("_", " ").title()}</h2>{note}{table(rows)}</section>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LibraryLens — SQL analytics</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f6f7f2;color:#19342c;font:15px/1.6 system-ui,sans-serif}}main{{max-width:1120px;margin:auto;padding:32px}}header{{border-bottom:1px solid #d6e1d5;padding-bottom:22px;display:flex;justify-content:space-between;gap:12px}}.brand{{font-weight:750;font-size:23px}}.tag{{font-size:12px;border:1px solid #bbcdb8;padding:6px 12px;border-radius:30px}}h1{{font-size:44px;letter-spacing:-1.5px;margin:30px 0 8px;line-height:1.15}}p,.note{{color:#5c7268}}.intro{{max-width:720px}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:28px 0}}.metric,section{{background:white;border:1px solid #dce5d8;border-radius:15px;padding:22px}}.metric span{{text-transform:capitalize;color:#60766b;font-size:12px}}.metric strong{{display:block;font-size:36px;line-height:1.4}}section{{margin-top:22px}}h2{{font-size:20px;margin:0 0 16px}}.bar-row{{display:grid;grid-template-columns:130px 1fr 40px;gap:18px;align-items:center;margin:17px 0}}.track{{background:#edf2e7;height:18px;border-radius:4px;overflow:hidden}}.track div{{background:#327052;height:100%;border-radius:4px}}.table-scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:11px;text-align:left;border-bottom:1px solid #e5ebe0}}th{{text-transform:capitalize;color:#60766b}}footer{{margin-top:25px;color:#60766b;font-size:12px}}@media(max-width:650px){{main{{padding:18px}}h1{{font-size:33px}}.metrics{{grid-template-columns:1fr 1fr;gap:10px}}.metric{{padding:14px}}.bar-row{{grid-template-columns:105px 1fr 25px;gap:10px;font-size:12px}}section{{padding:16px}}header{{flex-wrap:wrap}}}}
</style></head><body><main><header><div class="brand">LibraryLens</div><span class="tag">SQL / DATA ANALYSIS</span></header><h1>A library, seen through data.</h1><p class="intro">Explore borrowing patterns, inventory and overdue loans with six reproducible SQL reports. Every record is synthetic: this is a learning dataset, not a real campus report.</p><p class="note">Report date: {html.escape(report["as_of"])} · Seed: 42 · Python + SQLite · No external dependencies</p><div class="metrics">{cards}</div><section><h2>Borrowing by category</h2>{bars}<p class="note">Counts describe the generated dataset only. They are not evidence of real student preferences.</p></section>{sections}<footer>LibraryLens · Onkar Ghorpade · Synthetic data · Regenerate with python report.py</footer></main></body></html>'''


def build(output, as_of=AS_OF):
    validate_date(as_of)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with closing(database()) as connection:
        seed(connection)
        queries, columns = {}, {}
        for name in QUERIES:
            cursor = query_cursor(connection, name, as_of)
            columns[name] = [column[0] for column in cursor.description]
            queries[name] = [dict(row) for row in cursor]
    report = {"data_kind": "synthetic", "seed": 42, "as_of": as_of,
              "tables": {"books": 12, "members": 48}, "queries": queries}
    for name, rows in queries.items():
        with (output / f"{name}.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns[name])
            writer.writeheader()
            writer.writerows(rows)
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output / "dashboard.html").write_text(render_html(report), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build six SQL reports on deterministic synthetic library data.")
    parser.add_argument("--as-of", default=AS_OF, help="Report date within the synthetic archive")
    parser.add_argument("--output", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    try:
        report = build(args.output, args.as_of)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(report["queries"]["overview"][0], indent=2))
    print(f"Open {(args.output / 'dashboard.html').resolve()} in your browser.")
