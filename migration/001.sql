CREATE TABLE words (
    seq_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ulid TEXT NOT NULL UNIQUE,
    word TEXT NOT NULL UNIQUE,
    frequency INTEGER DEFAULT 0 NOT NULL,
    feedback REAL DEFAULT 0 NOT NULL
);

CREATE TABLE word_word (
    src TEXT NOT NULL,
    dst TEXT NOT NULL,
    UNIQUE (src, dst),
    FOREIGN KEY (src) REFERENCES words (ulid)
);
