import csv
import json
import os
import re
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from sudachipy import Dictionary

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from importer import Item

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("-f", "--input", type=Path)
    argparser.add_argument("-t", "--output", type=Path)
    args = argparser.parse_args()

    print(args)
    #remove_js = re.compile()

    with open(args.input) as f:
        content = re.sub(r'^[a-z0-9A-Z\.]+?\s=\s', "", f.read())
        print(content[:100])
        root = json.loads(content)

    paragraphs = []
    for i in root:
        if i["tweet"]["full_text"].startswith("RT"):
            continue
        else:
            txts = i["tweet"]["full_text"].split()
            paragraph = []
            for txt in txts:
                if txt.startswith("@"):
                    continue
                if txt.startswith("https://t.co"):
                    continue
                paragraph.append(txt)
            paragraphs.append(
                Item(
                    pubDate=datetime.strptime(
                        i["tweet"]["created_at"],
                        "%a %b %d %H:%M:%S %z %Y"
                    ),
                    description=" ".join(paragraph)
                )
            )

    wakachigaki_ps = []
    tokenizer = Dictionary().create()
    for p in paragraphs:
        p_arr = [m.surface() for m in tokenizer.tokenize(p.description)]
        wakachigaki_ps.append(Item(pubDate=p.pubDate, description=" ".join(p_arr)))

    print(wakachigaki_ps)
    with open("./data.csv", "a") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        for item in wakachigaki_ps:
            if len(item.description) < 1:
                continue
            writer.writerow([item.pubDate.timestamp(), item.description])
