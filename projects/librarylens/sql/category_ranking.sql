-- Rank ties equally; DENSE_RANK does not leave a gap after ties.
WITH demand AS (
  SELECT b.book_id, b.title, b.category, COUNT(l.loan_id) AS loans
  FROM books b LEFT JOIN loans l
    ON b.book_id = l.book_id AND l.borrowed_at <= :as_of
  GROUP BY b.book_id, b.title, b.category
)
SELECT *, DENSE_RANK() OVER (PARTITION BY category ORDER BY loans DESC) AS category_rank
FROM demand ORDER BY category, category_rank, title;
