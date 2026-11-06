SELECT b.book_id, b.title, b.total_copies,
       COUNT(l.loan_id) AS borrowed_copies,
       b.total_copies - COUNT(l.loan_id) AS available_copies
FROM books b LEFT JOIN loans l
  ON b.book_id = l.book_id AND l.borrowed_at <= :as_of
  AND (l.returned_at IS NULL OR l.returned_at > :as_of)
GROUP BY b.book_id, b.title, b.total_copies
ORDER BY available_copies, b.title;
