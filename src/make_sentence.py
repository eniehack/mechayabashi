import sqlite3
from pathlib import Path
from random import choices

from classopt import classopt, config


@classopt
class CLIOpt:
    db: Path = config(long=True)
    state: int = config(long=True, default=3)

def choice(db: sqlite3.Connection, word: list[str]) -> list[str]:
    print("choice word", f"{' '.join(word)} %")
    with db:
        res = db.execute(
            "SELECT word, frequency FROM words WHERE word LIKE ?",
            (f"{' '.join(word)} %",),
        ).fetchall()
    freq = [r["frequency"] for r in res]
    words = [r["word"] for r in res]
    return choices(words, weights=freq, k=1)[0].split()

def remove_padding(sentence: list[str]) -> list[str]:
    return [word for word in sentence if word not in ["__BEGIN__", "__END__"]]


args = CLIOpt.from_args()

db = sqlite3.connect(args.db)
db.row_factory = sqlite3.Row

sentence: list[str] = ["__BEGIN__"] * args.state
while len(sentence) < 1 or sentence[-1] != "__END__":
    new = choice(db, sentence[-args.state:])
    print("new", new)
    sentence.append(new[-1])
    #print(sentence)

print(sentence)
print(remove_padding(sentence))
