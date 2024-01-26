import csv
from argparse import ArgumentParser
from pathlib import Path

import markovify

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("-f", "--input", type=Path)
    argparser.add_argument("-t", "--output", type=Path)
    args = argparser.parse_args()

    paragraph_list = []
    with open(args.input) as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)
            paragraph_list.append(f"{row[1]} 。\n")

    text = "".join(paragraph_list)
    model = markovify.NewlineText(text, well_formed=False, state_size=3)

    with open(args.output, "w") as f:
        f.write(model.to_json())

