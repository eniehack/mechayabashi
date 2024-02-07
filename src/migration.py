import sqlite3
from pathlib import Path
from typing import Generator

from classopt import classopt, config


@classopt
class CLIOpt:
    db: Path = config(long=True)
    migration_dir: Path = config(long=True, default=Path("./migration"))

def migrate(db: sqlite3.Connection, sql_files: list | Generator) -> None:
    for path in sql_files:
        with open(path) as f:
            sql = f.read()
        with db:
            db.executescript(sql)

if __name__ == "__main__":
    args = CLIOpt.from_args()
    db = sqlite3.connect(args.db)
    migrate(db, args.migration_dir.glob("*.sql"))
    