import sqlite3
import json
import sys

import requests
from classopt import classopt, config
from make_sentence import make_sentence



@classopt
class CLIOpt:
    dic: str = config(long=True)
    host: str = config(long=True)
    token: str = config(long=True)
    state: int = config(long=True)

if __name__ == "__main__":
    args = CLIOpt.from_args()

    db = sqlite3.connect(args.dic)
    db.row_factory = sqlite3.Row

    resp = requests.post(
        f"https://{args.host}/api/notes/create",
        json={
            "i": args.token,
            "text": make_sentence(db, args.state),
            "visibility": "home",
        },
        headers={"Content-Type": "application/json"}
    )
    if resp.status_code != 200:
        exit(0)
    else:
        json.dump({"payload": resp.json(), "status": resp.status_code}, sys.stderr)
        exit(1)
