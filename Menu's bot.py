import os
import json
import random
from datetime import time

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

DISHES_PATH = "dishes.json"
HISTORY_PATH = "history.json"
HISTORY_KEEP = 20  # 直近何件を履歴として保持するか

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def pick_dish():
    dishes = load_json(DISHES_PATH)
    history = load_json(HISTORY_PATH)

    candidates = [d for d in dishes if d["name"] not in history]
    if not candidates:  # 全部出し切ったらリセット
        candidates = dishes
        history = []

    dish = random.choice(candidates)
    history.append(dish["name"])
    save_json(HISTORY_PATH, history[-HISTORY_KEEP:])
    return dish


def build_embed(dish):
    return discord.Embed(
        title=f"🍽 今日の料理: {dish['name']}",
        description=f"{dish['country']}（{dish['region']}）の料理です。",
        color=discord.Color.orange(),
    )


@tasks.loop(time=time(hour=0, minute=0))  # UTC 0:00 = JST 9:00
async def daily_dish():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"チャンネルが見つかりません: {CHANNEL_ID}")
        return
    dish = pick_dish()
    await channel.send(embed=build_embed(dish))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not daily_dish.is_running():
        daily_dish.start()


@bot.command()
async def dish(ctx):
    """手動で今日の一品を試す用コマンド"""
    d = pick_dish()
    await ctx.send(embed=build_embed(d))


bot.run(TOKEN)
