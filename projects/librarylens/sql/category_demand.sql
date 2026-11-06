-- LEFT JOIN retains categories whose books have no borrowing activity.
SELECT b.category, COUNT(l.loan_id) AS loans,
       COUNT(DISTINCT l.member_id) AS borrowers
FROM books b
LEFT JOIN loans l ON l.book_id = b.book_id AND l.borrowed_at <= :as_of
GROUP BY b.category
ORDER BY loans DESC, b.category;
