import markovify
from argparse import ArgumentParser
from pathlib import Path

argparser = ArgumentParser()
argparser.add_argument("-d", "--dict", type=Path)
args = argparser.parse_args()

with open(args.dict, 'r') as f:
    text_model = markovify.Text.from_json(f.read())

for i in range(10):
    print(text_model.make_sentence().replace(" ", ""))
