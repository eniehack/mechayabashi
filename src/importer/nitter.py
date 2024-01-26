import csv
from datetime import datetime
from html.parser import HTMLParser
from xml.sax import ContentHandler, make_parser

from sudachipy import Dictionary

from .importer import Item


class NitterContentHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tokenizer = Dictionary().create()
        self.inside_p_tag = False
        self.p_text = ""
        self.p_texts = []

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            self.inside_p_tag = True
        else:
            self.inside_p_tag = False

    def handle_endtag(self, tag):
        if tag == "p":
            self.inside_p_tag = False
            for m in self.tokenizer.tokenize(self.p_text):
                self.p_texts.append(m.surface()) 
            self.p_text = ""  # テキストを取得したらリセット

    def handle_data(self, data):
        if self.inside_p_tag:
            self.p_text += data

class NitterRSSHandler(ContentHandler):
    def __init__(self):
        self.current_element = ""
        self.is_target_item = False
        self.current_item = None
        self.items = []

    def startElement(self, name, attrs):
        self.current_element = name
        if name == "item":
            self.is_target_item = False
            self.current_item = Item(pubDate=None, description="")

    def endElement(self, name):
        if name == "item" and self.is_target_item:
            parser = NitterContentHTMLParser()
            parser.feed(self.current_item.description)
            self.current_item.description = " ".join(parser.p_texts)
            self.items.append(self.current_item)
        self.current_element = ""

    def characters(self, content):
        if self.current_element == "dc:creator" and content == "@eniehack":
            self.is_target_item = True
        elif self.current_element == "pubDate" and self.is_target_item:
            self.current_item.pubDate = datetime.strptime(
                content,
                "%a, %d %b %Y %H:%M:%S %Z"
            )
        elif self.current_element == "description" and self.is_target_item:
            self.current_item.description += content

if __name__ == "__main__":
    rss_content = """"""

    handler = NitterRSSHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.feed(rss_content)

    # 抽出した結果を表示
    with open("./data.csv", "a") as f:
        cw = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        for item in handler.items:
            cw.writerow([item.pubDate.timestamp(), item.description])
