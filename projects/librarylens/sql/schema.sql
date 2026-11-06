PRAGMA foreign_keys = ON;
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    total_copies INTEGER NOT NULL CHECK (total_copies > 0)
);
CREATE TABLE members (
    member_id TEXT PRIMARY KEY,
    department TEXT NOT NULL
);
CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(book_id),
    member_id TEXT NOT NULL REFERENCES members(member_id),
    borrowed_at TEXT NOT NULL,
    due_at TEXT NOT NULL,
    returned_at TEXT,
    CHECK (due_at >= borrowed_at),
    CHECK (returned_at IS NULL OR returned_at >= borrowed_at)
);
CREATE INDEX loans_book_dates ON loans(book_id, borrowed_at, returned_at);
CREATE INDEX loans_member ON loans(member_id);
