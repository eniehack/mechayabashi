from pathlib import Path

from classopt import classopt, config
from discord import Client, Intents, Interaction, app_commands
from make_sentence import make_sentence
import sqlite3
from sudachipy import Dictionary


@classopt
class CLIArgs:
    token: str = config(long=True, required=True)
    dic: Path = config(long=True, required=True)
    state: int = config(long=True, default=3)

args = CLIArgs.from_args()
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)
tree = app_commands.CommandTree(client)

tokenizer = Dictionary().create()
db = sqlite3.connect(args.dic)
db.row_factory = sqlite3.Row

@tree.command(name="generate", description="マルコフ連鎖で文章を生成します")
async def generate(ctx: Interaction):
    await ctx.response.send_message(
        make_sentence(db, args.state)
    )

@tree.command(name="wakatigaki", description="分かち書きします")
@app_commands.describe(
    txt="分かち書きする文"
)
async def wakatigaki(ctx: Interaction, txt: str):
    await ctx.response.send_message(
        " ".join([m.surface() for m in tokenizer.tokenize(txt)])
    )

@client.event
async def on_ready():
    print("ready")
    await tree.sync()

client.run(args.token)