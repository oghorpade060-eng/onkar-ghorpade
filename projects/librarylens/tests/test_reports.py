import csv
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from report import AS_OF, build, database, run_query, seed, validate_date


class ReportsTest(unittest.TestCase):
    def setUp(self):
        self.db = database()
        self.addCleanup(self.db.close)
        self.db.execute("INSERT INTO books VALUES (1, 'Test book', 'Programming', 3)")
        self.db.execute("INSERT INTO books VALUES (2, 'Never borrowed', 'Systems', 1)")
        self.db.execute("INSERT INTO members VALUES ('M001', 'AI & DS')")

    def loan(self, loan_id, borrowed, due, returned=None):
        self.db.execute("INSERT INTO loans VALUES (?,1,'M001',?,?,?)", (loan_id, borrowed, due, returned))

    def test_due_today_is_not_overdue(self):
        self.loan(1, '2026-10-01', AS_OF)
        self.loan(2, '2026-10-01', '2026-10-31')
        rows = run_query(self.db, 'overdue_loans')
        self.assertEqual([(row['loan_id'], row['days_overdue']) for row in rows], [(2, 1)])

    def test_later_return_is_still_open_in_historical_report(self):
        self.loan(1, '2026-06-01', '2026-06-10', '2026-06-20')
        self.assertEqual(run_query(self.db, 'overview', '2026-06-15')[0]['open_loans'], 1)
        self.assertEqual(run_query(self.db, 'overview', '2026-06-20')[0]['open_loans'], 0)

    def test_future_borrow_does_not_enter_report(self):
        self.loan(1, '2026-07-01', '2026-07-15')
        self.assertEqual(run_query(self.db, 'overview', '2026-06-01')[0]['total_loans'], 0)

    def test_left_join_keeps_unused_books_and_categories(self):
        self.loan(1, '2026-10-01', '2026-10-15')
        categories = {row['category']: row['loans'] for row in run_query(self.db, 'category_demand')}
        self.assertEqual(categories, {'Programming': 1, 'Systems': 0})
        unused = next(row for row in run_query(self.db, 'inventory') if row['book_id'] == 2)
        self.assertEqual(unused['available_copies'], 1)

    def test_window_function_retains_empty_months(self):
        self.loan(1, '2026-05-01', '2026-05-15', '2026-05-14')
        self.loan(2, '2026-07-01', '2026-07-15', '2026-07-14')
        rows = run_query(self.db, 'monthly_activity', '2026-07-20')
        self.assertEqual([row['loans'] for row in rows], [1, 0, 1])
        self.assertEqual([row['change_in_loans'] for row in rows], [None, -1, 1])

    def test_relational_constraints(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO loans VALUES (1,99,'M001','2026-10-01','2026-10-15',NULL)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.loan(2, '2026-10-15', '2026-10-01')

    def test_bad_dates_are_rejected(self):
        for value in ['2026-02-30', '2027-01-01', "2026-06-01'; DROP TABLE books;--"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_date(value)

    def test_generated_inventory_never_goes_negative(self):
        connection = database()
        self.addCleanup(connection.close)
        seed(connection)
        days = [row[0] for row in connection.execute('SELECT DISTINCT borrowed_at FROM loans')]
        for day in days:
            self.assertTrue(all(row['available_copies'] >= 0 for row in run_query(connection, 'inventory', day)))
        overview = run_query(connection, 'overview')[0]
        self.assertEqual(sum(row['loans'] for row in run_query(connection, 'monthly_activity')), overview['total_loans'])
        self.assertEqual(len(run_query(connection, 'overdue_loans')), overview['overdue_loans'])

    def test_reproducible_reports_and_empty_csv_replacement(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            first = build(output)
            self.assertEqual(first, build(output))
            self.assertIn('synthetic', (output / 'dashboard.html').read_text())
            build(output, '2026-05-01')
            with (output / 'overdue_loans.csv').open(newline='') as stream:
                rows = list(csv.reader(stream))
            self.assertEqual(len(rows), 1)
            self.assertIn('days_overdue', rows[0])


if __name__ == '__main__':
    unittest.main()
