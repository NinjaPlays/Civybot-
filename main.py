import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

# --- Utility functions ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Bot events ---
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")

# --- Commands ---
@bot.command()
async def balance(ctx):
    """Check your gold and resources."""
    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data:
        data[user_id] = {"gold": 0, "wood": 0, "stone": 0, "iron": 0, "last_daily": None}
        save_data(data)

    stats = data[user_id]
    await ctx.send(f"💰 Gold: {stats['gold']}\n🌲 Wood: {stats['wood']}\n🪨 Stone: {stats['stone']}\n⛓ Iron: {stats['iron']}")

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def quickmine(ctx, resource: str):
    """Mine 10 of a resource (30s cooldown)."""
    resource = resource.lower()
    if resource not in ["wood", "stone", "iron"]:
        await ctx.send("You can only mine: wood, stone, or iron.")
        return

    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data:
        data[user_id] = {"gold": 0, "wood": 0, "stone": 0, "iron": 0, "last_daily": None}

    data[user_id][resource] += 10
    save_data(data)
    await ctx.send(f"{ctx.author.mention} mined 10 {resource} ⛏")

@bot.command()
async def daily(ctx, resource: str):
    """Claim 100 of a chosen resource every 24h."""
    resource = resource.lower()
    if resource not in ["wood", "stone", "iron"]:
        await ctx.send("You can only claim: wood, stone, or iron.")
        return

    data = load_data()
    user_id = str(ctx.author.id)
    now = datetime.utcnow()

    if user_id not in data:
        data[user_id] = {"gold": 0, "wood": 0, "stone": 0, "iron": 0, "last_daily": None}

    last_daily = data[user_id]["last_daily"]
    if last_daily and datetime.fromisoformat(last_daily) + timedelta(hours=24) > now:
        await ctx.send("⏳ You already claimed your daily reward. Try again later!")
        return

    data[user_id][resource] += 100
    data[user_id]["last_daily"] = now.isoformat()
    save_data(data)
    await ctx.send(f"{ctx.author.mention} claimed 100 {resource} 🎉")

# --- Run bot ---
bot.run(os.getenv("DISCORD_TOKEN"))
