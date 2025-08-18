import sqlite3
from pathlib import Path
import math

from classopt import classopt, config
from discord import Client, Intents, Interaction, Member, Reaction, User, app_commands
from make_sentence import make_sentence_bayesian, generate_random_choice_percent
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
random_choice_percent = generate_random_choice_percent(db)

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
    await ctx.response.defer()
    await ctx.followup.send(
        make_sentence_bayesian(db, args.state, random_choice_percent)
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

def update_weight(old: float, current: float, alpha = 0.1):
    return (1 - alpha) * old + alpha * current

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
    tokens = ["__BEGIN__"] * args.state
    # tokens.extend([m.surface() for m in tokenizer.tokenize(msg.content) if m.surface() not in [" ", ""]])
    tokens.extend([i for i in msg.content.split(chr(0x2063))])
    tokens.extend(["__END__"] * args.state)

    results = []    
    with db:
        for token in ngrams(tokens, args.state + 1):
            results.append(
                db.execute(
                    "SELECT ulid, word, frequency, feedback FROM words WHERE word = ?;",
                    (' '.join(token),),
                ).fetchone()
            )
    rev_freqs: list[float] = [1.0/r['frequency'] for r in results]
    sum_w = math.fsum(rev_freqs)
    for r in results:
        weight = 1 / (sum_w * r['frequency'])
        if reaction.emoji in ["❌"]:
            with db:
                db.execute(
                    "UPDATE words SET feedback = ? WHERE ulid = ?;",
                    (update_weight(r["feedback"], -1 * weight), r["ulid"])
                )
                print("downvoted", r['word'], update_weight(r["feedback"], -1 * weight))
        else:
            with db:
                db.execute(
                    "UPDATE words SET feedback = ? WHERE ulid = ?;",
                    (update_weight(r["feedback"], weight), r["ulid"])
                )
                print("upvoted", r['word'], update_weight(r["feedback"], weight))
        


client.run(args.token)
