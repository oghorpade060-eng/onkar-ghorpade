-- A book due today is not overdue yet. Historical reports ignore later returns.
SELECT l.loan_id, l.member_id, m.department, b.title, l.due_at,
       CAST(julianday(:as_of) - julianday(l.due_at) AS INTEGER) AS days_overdue
FROM loans l
JOIN members m ON m.member_id = l.member_id
JOIN books b ON b.book_id = l.book_id
WHERE l.borrowed_at <= :as_of AND l.due_at < :as_of
  AND (l.returned_at IS NULL OR l.returned_at > :as_of)
ORDER BY days_overdue DESC, l.loan_id;
