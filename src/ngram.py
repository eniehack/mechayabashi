import csv
import sqlite3
from collections import Counter
from pathlib import Path

from classopt import classopt, config
from nltk import ngrams
from ulid import ULID

from migration import migrate

BEGIN = "__BEGIN__"
END = "__END__"

@classopt
class CLIOpt:
    csv: Path = config(long=True)
    db: Path = config(long=True)
    migrate: bool = config(long=True, default=False)
    migrate_dir: Path = config(long=True, default=Path("./migration"))
    state: int = config(long=True, default=3)

def fetch_wordID(db: sqlite3.Connection, node: tuple) -> str:
    with db:
        res = db.execute(
            "SELECT ulid FROM words WHERE word = ?",
            (" ".join(node),)
        ).fetchone()
    return res[0]

def insert_node(db: sqlite3.Connection, counter: Counter, n: int) -> None:
    with db:
        db.executemany(
            """
            INSERT INTO words (ulid, word, frequency, feedback)
            SELECT :ulid, :word, :freq, :fb
            WHERE NOT EXISTS (
                SELECT * FROM words WHERE word = :word
            );
            """,
            [
                {
                    "ulid": str(ULID()),
                    "word": " ".join(node),
                    "freq": counter[node],
                    "fb": 0.0,
                }
                for node in counter
            ]
        )


# def insert_edge(db: sqlite3.Connection, counter: Counter, state: int):
#     db.row_factory = sqlite3.Row
#     for node in counter:
#         with db:
#             res = db.execute(
#                 """
#                 SELECT ulid, word, frequency FROM words
#                 WHERE word LIKE ?
#                   AND word != ?;
#                 """,
#                 (f"{' '.join(node[-state:])}%", ' '.join(node))
#             ).fetchall()
#         # neighbors = [(r["ulid"], r["word"], r["frequency"]) for r in res]
#         # print(neighbors)

def default_encoder(encoder, value):
    encoder.encode(vars(value))

if __name__ == "__main__":
    args = CLIOpt.from_args()
    paragraph_list = []
    with open(args.csv) as f:
        reader = csv.reader(f)
        for row in reader:
            begin = [BEGIN] * (args.state)
            end = [END] * (args.state)
            paragraph_list.append(f'{" ".join(begin)} {row[1]} {" ".join(end)}')
    wakachigaki_pl = [p.split() for p in paragraph_list]
    #print(wakachigaki_pl)
    words: list[tuple] = []
    for p in wakachigaki_pl:
        words.extend(list(ngrams(p, args.state + 1)))
        
    #print(ngrams)
    counter = Counter(words)
    #print(counter)

    db = sqlite3.connect(args.db)
    db.row_factory = sqlite3.Row
    if args.migrate:
        with db:
            migrate(db, args.migrate_dir.glob("*.sql"))
    insert_node(db, counter, args.state)
    #insert_edge(db, counter, args.state)