import sqlite3
from pathlib import Path
from random import choices, random

from classopt import classopt, config


@classopt
class CLIOpt:
    db: Path = config(long=True)
    state: int = config(long=True, default=3)

def choice(db: sqlite3.Connection, word: list[str]) -> list[str]:
    #print("choice word", f"{' '.join(word)} %")
    with db:
        res = db.execute(
            "SELECT word, frequency, feedback FROM words WHERE word LIKE ?",
            (f"{' '.join(word)} %",),
        ).fetchall()
    words = [r["word"] for r in res]
    
    if random() <= 0.2:
        return choices(words, k=1)[0].split()
    freq = [r["frequency"] for r in res]
    feedbacks = [r["feedback"] for r in res]
    w = [(i[0] * 0.8 + i[1] * 0.2) / len(words) for i in zip(freq, feedbacks)]
    return choices(words, weights=w, k=1)[0].split()

def remove_padding(sentence: list[str]) -> list[str]:
    return [word for word in sentence if word not in ["__BEGIN__", "__END__"]]

def concat(l: list[str]) -> str:
    asc = [s.isascii() for s in l]
    s = l[0]
    for i in range(1,len(l)):
        if asc[i-1] == asc[i]:
                s += l[i]
        else:
                s += " " 
                s += l[i]
    return s

def make_sentence(db: sqlite3.Connection, state: int) -> str:
    sentence: list[str] = ["__BEGIN__"] * state
    while sentence[-state] != "__END__":
        new = choice(db, sentence[-state:])
        #print("new", new)
        sentence.append(new[-1])
        #print(sentence)
    return concat(remove_padding(sentence))

if __name__ == "__main__":
    args = CLIOpt.from_args()

    db = sqlite3.connect(args.db)
    db.row_factory = sqlite3.Row
    print(make_sentence(db, args.state))


