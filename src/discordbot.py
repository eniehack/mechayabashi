import sqlite3
from pathlib import Path

from classopt import classopt, config
from discord import Client, Intents, Interaction, Member, Reaction, User, app_commands
from make_sentence import make_sentence
from nltk import ngrams
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

@tree.command(name="help", description="メカやばしの使い方を説明します")
async def help(ctx: Interaction):
    await ctx.response.send_message(
        """
        メカやばしはなかやばしのツイートから文章を生成するbotです。
        さらに、生成した文章にリアクションを付けることでフィードバックすることができます。
        ❌を付けると「良くない文である」と、それ以外のリアクションは「良い文である」とそれぞれフィードバックします。
        """
    )

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

@client.event
async def on_reaction_add(reaction: Reaction, user: Member | User):
    msg = reaction.message
    if msg.author == user:
        return
    if not msg.author.id == client.user.id:
        return
    if msg.content.startswith(
        "メカやばしはなかやばしのツイートから文章を生成するbotです。"
    ):
        return

    for token in ngrams(
        [m.surface() for m in tokenizer.tokenize(msg.content)],
        args.state + 1
    ):
        print(token)
        with db:
            res = db.execute(
                "SELECT ulid, feedback FROM words WHERE word = ?;",
                (" ".join(token),)
            ).fetchone()
        if reaction.emoji in ["❌"]:
            with db:
                db.execute(
                    "UPDATE words SET feedback = ? WHERE ulid = ?;",
                    (res["feedback"] - 1, res["ulid"])
                )
                print("downvoted", " ".join(token), res["feedback"] - 1)
        else:
            with db:
                db.execute(
                    "UPDATE words SET feedback = ? WHERE ulid = ?;",
                    (res["feedback"] + 1, res["ulid"])
                )
                print("upvoted", " ".join(token), res["feedback"] + 1)
        


client.run(args.token)