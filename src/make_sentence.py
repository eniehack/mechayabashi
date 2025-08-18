import sqlite3
from pathlib import Path
from random import choices, random

from classopt import classopt, config


@classopt
class CLIOpt:
    db: Path = config(long=True)
    state: int = config(long=True, default=3)

def generate_random_choice_percent(db) -> float:
    with db:
        nonzero_row_count = db.execute(
            "SELECT count(*) as res FROM words WHERE feedback != 0",
        ).fetchone()
        row_count = db.execute(
            "SELECT count(*) as res FROM words",
        ).fetchone()
    nonzero_row_percent = nonzero_row_count["res"] / row_count["res"]
    random_percent = 0.2 if 0.5 <= nonzero_row_percent else (0.8 - nonzero_row_percent)
    return random_percent

def choice_by_bayesian(db, word: list[str], random_percent: float, beta=1.5, baseline_factor=0.5) -> list[str]:
    """ベイズ的アプローチで次の単語を選択"""
    with db:
        res = db.execute(
            "SELECT word, frequency, feedback FROM words WHERE word LIKE ?",
            (f"{' '.join(word)} %",),
        ).fetchall()
    
    if not res:
        return []
    
    words = [r["word"] for r in res]
    
    # 20%の確率でランダム選択（元のロジックを保持）
    if random() <= random_percent:
        return choices(words, k=1)[0].split()
    
    # ベースライン計算（全体平均の半分）
    total_reactions = sum(r["feedback"] for r in res)
    total_freq = sum(r["frequency"] for r in res)
    baseline = (total_reactions / total_freq * baseline_factor) if total_freq > 0 else 0.1
    
    # ベイズ的重み計算
    weights = []
    for r in res:
        freq, feedback = r["frequency"], r["feedback"]
        
        # 事前確率（その文脈での出現確率）
        prior = freq / total_freq if total_freq > 0 else 0
        
        # 尤度（リアクション率 + ベースライン）
        reaction_rate = feedback / freq if freq > 0 else 0
        likelihood = reaction_rate + baseline
        
        # ベイズ重み = 事前確率 × (尤度 + ベースライン)^beta
        weight = prior * ((likelihood + 1.0) ** beta)
        weights.append(weight)
    
    return choices(words, weights=weights, k=1)[0].split()

def make_sentence_bayesian(db: sqlite3.Connection, state: int, random_choice_percent, beta=1.5) -> str:
    """ベイズ的アプローチで文章生成"""
    sentence: list[str] = ["__BEGIN__"] * state
    while sentence[-state] != "__END__":
        new = choice_by_bayesian(db, sentence[-state:], random_choice_percent, beta=beta)
        if not new:  # 候補がない場合は終了
            break
        sentence.append(new[-1])
    return concat(remove_padding(sentence))

def choice_by_geometric_mean(db: sqlite3.Connection, word: list[str]) -> list[str]:
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
    return chr(0x2063).join(l)
    # asc = [s.isascii() for s in l]
    # s = l[0]
    # for i in range(1,len(l)):
    #     if asc[i-1] == asc[i]:
    #             s += l[i]
    #     else:
    #             s += " " 
    #             s += l[i]
    # return s

def make_sentence(db: sqlite3.Connection, state: int) -> str:
    sentence: list[str] = ["__BEGIN__"] * state
    while sentence[-state] != "__END__":
        new = choice_by_geometric_mean(db, sentence[-state:])
        #print("new", new)
        sentence.append(new[-1])
        #print(sentence)
    return concat(remove_padding(sentence))

if __name__ == "__main__":
    args = CLIOpt.from_args()

    db = sqlite3.connect(args.db)
    db.row_factory = sqlite3.Row
    print(make_sentence(db, args.state))


