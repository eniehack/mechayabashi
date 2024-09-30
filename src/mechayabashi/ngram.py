import csv
import sqlite3
from collections import Counter
from pathlib import Path
from math import log

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

def tfidf(w_freq_sum: int, w_freq: int, doc_size) -> float:
    return w_freq * log(doc_size - w_freq/w_freq) / w_freq_sum

def insert_node(db: sqlite3.Connection, n_counter: Counter) -> None:
    with db:
        db.executemany(
            """
            INSERT INTO words (ulid, word, feedback)
            SELECT :ulid, :word, :fb
            WHERE NOT EXISTS (
                SELECT * FROM words WHERE word = :word
            );
            """,
            [
                {
                    "ulid": str(ULID()),
                    "word": " ".join(node),
                    "fb": 0.0,
                }
                for node in n_counter
            ]
        )


def insert_tfidf(db: sqlite3.Connection, nky_counter: Counter, docs_size: int, gen_counter: Counter) -> None:
    tfidf_scores: dict[tuple, float] = {}
    all = sum(nky_counter.values())
    for i in nky_counter:
        tfidf_scores[i] = tfidf(all, nky_counter[i], docs_size)
    with db:
        db.executemany(
            "UPDATE words SET tfidf = ? WHERE word = ?",
            [(v, " ".join(k)) for k, v in tfidf_scores.items()]
        )

def default_encoder(encoder, value):
    encoder.encode(vars(value))

if __name__ == "__main__":
    args = CLIOpt.from_args()
    paragraph_list: list[str] = []
    with open(args.csv) as f:
        reader = csv.reader(f)
        for row in reader:
            begin = [BEGIN] * (args.state)
            end = [END] * (args.state)
            paragraph_list.append(f'{" ".join(begin)} {row[1]} {" ".join(end)}')
    docs_size = len(paragraph_list)
    wakachigaki_pl = [p.split() for p in paragraph_list]
    #print(wakachigaki_pl)
    words: list[tuple[int, list[tuple]]] = []
    for i, p in enumerate(wakachigaki_pl):
        words.append(i, list(ngrams(p, args.state + 1))))
    
    l = len(words)
    #print(ngrams)
    n_counter = Counter(words)
    #print(counter)

    db = sqlite3.connect(args.db)
    db.row_factory = sqlite3.Row
    if args.migrate:
        with db:
            migrate(db, args.migrate_dir.glob("*.sql"))
    insert_node(db, n_counter)
    insert_tfidf(db, n_counter, docs_size, n_counter)