import discord
from discord.ext import commands
import os


# docker-composeから渡された環境変数の設定
TOKEN = os.getenv("TOKEN") 
GUILDS = [int(v) for v in os.getenv("GUILDS").split(",")]
# intentsの設定（エラーが出るまで基本defaultで良いです） 
intents = discord.Intents.default()
intents.message_content = True

# debug_guildsは公開BOTの場合は必要ないです
bot = commands.Bot(
    command_prefix='!',
    debug_guilds=GUILDS,
    intents=intents
)

# botが動いてるか確認するだけのヤツ
@bot.event
async def on_ready():
    print(f"Bot名:{bot.user} On ready!!")

# cogsディレクトリにあるsub.pyを読み込む処理です
@bot.event
async def setup_hook():
    await bot.load_extension("cogs.file_viewer")

# botの起動
bot.run(TOKEN)
