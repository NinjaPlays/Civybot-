import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents, help_command=None)

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

def ensure_user(data, user_id):
    """Make sure a user exists in the data with starter gold."""
    if user_id not in data:
        data[user_id] = {
            "gold": 100,   # Starter gold
            "wood": 0,
            "stone": 0,
            "iron": 0,
            "last_daily": None
        }
    return data

# --- Bot events ---
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")

# --- Custom help command ---
@bot.command()
async def help(ctx):
    """Show all available commands."""
    help_text = (
        "🤖 **CivyBot Commands** (use by mentioning me, e.g. `@CivyBot balance`)\n\n"
        "• `@CivyBot balance` → Check your gold and resources.\n"
        "• `@CivyBot quickmine <resource>` → Mine 10 of wood/stone/iron (30s cooldown).\n"
        "• `@CivyBot daily <resource>` → Claim 100 of wood/stone/iron (once every 24h).\n"
    )
    await ctx.send(help_text)

# --- Commands ---
@bot.command()
async def balance(ctx):
    """Check your gold and resources."""
    data = load_data()
    user_id = str(ctx.author.id)
    data = ensure_user(data, user_id)
    save_data(data)

    stats = data[user_id]
    await ctx.send(
        f"💰 Gold: {stats['gold']}\n"
        f"🌲 Wood: {stats['wood']}\n"
        f"🪨 Stone: {stats['stone']}\n"
        f"⛓ Iron: {stats['iron']}"
    )

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
    data = ensure_user(data, user_id)

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
    data = ensure_user(data, user_id)
    now = datetime.utcnow()

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
