import os
import discord
from discord.ext import commands, tasks
import json, random
from datetime import datetime, time

CHANNEL_ID = 1544438399505793064 # 投稿先チャンネルID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def pick_dish():
    dishes = load_json("dishes.json")
    history = load_json("history.json")  # 直近出した name のリスト

    candidates = [d for d in dishes if d["name"] not in history]
    if not candidates:  # 全部出し切ったらリセット
        candidates = dishes
        history = []

    dish = random.choice(candidates)
    history.append(dish["name"])
    save_json("history.json", history[-20:])  # 直近20件だけ保持
    return dish

@tasks.loop(time=time(hour=9, minute=0))  # 毎日9:00 (サーバーのタイムゾーン基準)
async def daily_dish():
    channel = bot.get_channel(CHANNEL_ID)
    dish = pick_dish()
    embed = discord.Embed(
        title=f"🍽 今日の料理: {dish['name']}",
        description=f"{dish['country']}（{dish['region']}）の料理です。",
        color=discord.Color.orange()
    )
    await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not daily_dish.is_running():
        daily_dish.start()

bot.run(os.getenv("BOT_TOKEN"))
