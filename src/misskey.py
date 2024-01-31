from classopt import classopt, config
from markovify import Text
import requests

@classopt
class CLIOpt:
    dic: str = config(long=True)
    host: str = config(long=True)
    token: str = config(long=True)

if __name__ == "__main__":
    args = CLIOpt.from_args()
    
    with open(args.dic, 'r') as f:
        text_model = Text.from_json(f.read())

    resp = requests.post(
        f"https://{args.host}/api/notes/create",
        json={
            "i": args.token,
            "text": text_model.make_sentence(),
            "visibility": "home",
        },
        headers={"Content-Type": "application/json"}
    )
    print(resp)
