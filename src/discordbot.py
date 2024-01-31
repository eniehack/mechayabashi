from discord import app_commands, Intents, Client, Interaction
from classopt import classopt, config
from pathlib import Path
import markovify

@classopt
class CLIArgs:
    token: str = config(long=True, required=True)
    dic: Path = config(long=True, required=True)

args = CLIArgs.from_args()
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)
tree = app_commands.CommandTree(client)

with open(args.dic, 'r') as f:
    text_model = markovify.Text.from_json(f.read())

@tree.command(name="generate", description="マルコフ連鎖で文章を生成します")
async def generate(ctx: Interaction):
    await ctx.response.send_message(text_model.make_sentence().replace(" ", ""))

@client.event
async def on_ready():
    print("ready")
    await tree.sync()

client.run(args.token)