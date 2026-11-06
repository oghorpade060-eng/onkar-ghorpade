-- The report date is a bound value, never inserted into SQL text.
SELECT COUNT(*) AS total_loans,
       COUNT(DISTINCT member_id) AS borrowing_members,
       COALESCE(SUM(CASE WHEN returned_at IS NULL OR returned_at > :as_of THEN 1 ELSE 0 END), 0) AS open_loans,
       COALESCE(SUM(CASE WHEN due_at < :as_of AND (returned_at IS NULL OR returned_at > :as_of) THEN 1 ELSE 0 END), 0) AS overdue_loans
FROM loans
WHERE borrowed_at <= :as_of;
