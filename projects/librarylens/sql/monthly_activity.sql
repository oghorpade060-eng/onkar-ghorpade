-- Include zero-loan months, then compare each month with its predecessor.
WITH RECURSIVE months(month) AS (
  SELECT date('2026-05-01')
  UNION ALL
  SELECT date(month, '+1 month') FROM months
  WHERE month < date(:as_of, 'start of month')
), counts AS (
  SELECT months.month, COUNT(loans.loan_id) AS loans
  FROM months LEFT JOIN loans
    ON strftime('%Y-%m', loans.borrowed_at) = strftime('%Y-%m', months.month)
    AND loans.borrowed_at <= :as_of
  GROUP BY months.month
)
SELECT month, loans, LAG(loans) OVER (ORDER BY month) AS previous_month,
       loans - LAG(loans) OVER (ORDER BY month) AS change_in_loans
FROM counts ORDER BY month;
