# discord bot.py

import random
import asyncio
import discord
from discord.ext import commands

# ========= CONFIG =========
TOKEN = "MTQ0MzI3MTM4ODQyNDE3NTc5OA.GLVQBd.Ws_EZO2LmggQWKWZK64nnzO-rjCernIpb7EmYU"  # <-- paste your real bot token here
PREFIX = "!"

intents = discord.Intents.default()
intents.message_content = True  # you already enabled this in the portal

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# bad words list (edit if you want)
BAD_WORDS = ["badword1", "badword2", "stupid"]

# simple spam tracker: user_id -> (last_message, count)
spam_tracker = {}


# ========= EVENTS =========

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")


@bot.event
async def on_message(message: discord.Message):
    # don't react to your own bot
    if message.author == bot.user:
        return

    # ----- bad word filter -----
    lowered = message.content.lower()
    if any(bad_word in lowered for bad_word in BAD_WORDS):
        try:
            await message.delete()
        except discord.Forbidden:
            pass

        warning = await message.channel.send(
            f"{message.author.mention} hey! That word is not allowed here. 🛑"
        )
        await asyncio.sleep(5)
        await warning.delete()
        return  # stop here, don't process commands from this message

    # ----- super simple spam check -----
    user_id = message.author.id
    text = message.content

    if user_id not in spam_tracker:
        spam_tracker[user_id] = (text, 1)
    else:
        last_text, count = spam_tracker[user_id]
        if text == last_text:
            count += 1
        else:
            count = 1

        spam_tracker[user_id] = (text, count)

        if count >= 3 and len(text) > 0:
            warning = await message.channel.send(
                f"{message.author.mention} chill with the spam pls 😅"
            )
            await asyncio.sleep(5)
            await warning.delete()

    # VERY IMPORTANT: let commands like !ping, !commands, etc run
    await bot.process_commands(message)


# ========= SIMPLE COMMANDS =========

@bot.command(name="ping")
async def ping(ctx: commands.Context):
    """Check if the bot is alive."""
    await ctx.send(f"Pong! 🏓 Latency: {round(bot.latency * 1000)} ms")


# ========= FUN COMMANDS =========

@bot.command(name="slap")
async def slap(ctx: commands.Context, member: discord.Member = None):
    """Slap someone 👋"""
    if member is None:
        await ctx.send("Who do you want to slap? Use: `!slap @user`")
        return
    await ctx.send(f"{ctx.author.mention} slapped {member.mention} 💥")


@bot.command(name="hug")
async def hug(ctx: commands.Context, member: discord.Member = None):
    """Give someone a hug 🤗"""
    if member is None:
        await ctx.send("Who do you want to hug? Use: `!hug @user`")
        return
    await ctx.send(f"{ctx.author.mention} gives {member.mention} a big hug 🤗💖")


EIGHT_BALL_ANSWERS = [
    "Yes, for sure ✅",
    "Nah, no way ❌",
    "Maybe… not sure 😶",
    "Ask again later ⏳",
    "Definitely yes 😎",
    "I don't think so 🤔",
]


@bot.command(name="8ball")
async def eight_ball(ctx: commands.Context, *, question: str = None):
    """Magic 8ball 🎱"""
    if question is None:
        await ctx.send("Ask me a question like: `!8ball will I be rich?`")
        return

    answer = random.choice(EIGHT_BALL_ANSWERS)
    await ctx.send(f"🎱 **Question:** {question}\n**Answer:** {answer}")


ROASTS = [
    "I would explain it to you, but I left my crayons at home 😂",
    "Your brain has ping like 9999ms 💀",
    "You're the reason the loading bar exists 😭",
    "Somewhere out there, a tree is working hard to replace your oxygen…",
    "I consider you my Sun. Now, please get 93 million miles away from here.",
    "If laughter is the best medicine, your face must be curing the world.",
    "You’re not simply a drama queen/king. You’re the whole royal family.",
    "You have a face that would make onions cry. ",
    "I look at you and think, “Two billion years of evolution, for this?”",
]


@bot.command(name="roast")
async def roast(ctx: commands.Context, member: discord.Member = None):
    """Playful roast 🔥 (don't be mean for real)"""
    if member is None:
        member = ctx.author

    roast_line = random.choice(ROASTS)
    await ctx.send(f"{member.mention} {roast_line}")


@bot.command(name="userinfo")
async def userinfo(ctx: commands.Context, member: discord.Member = None):
    """Show info about a user."""
    if member is None:
        member = ctx.author

    embed = discord.Embed(
        title=f"User info: {member}",
        description=f"ID: {member.id}",
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(
        name="Joined server",
        value=str(member.joined_at)[:19],
        inline=False
    )
    embed.add_field(
        name="Account created",
        value=str(member.created_at)[:19],
        inline=False
    )
    await ctx.send(embed=embed)


# ========= COMMAND LIST (YOUR !commands) =========

@bot.command(name="cmd", aliases=["commands", "c"])
async def commands_list(ctx: commands.Context):
    """Show all commands for this bot."""
    lines = [
        "**Here are my commands:**",
        "`!ping` - check if the bot is alive",
        "`!slap @user` - slap someone 💥",
        "`!hug @user` - give someone a hug 🤗",
        "`!8ball question` - magic 8ball 🎱",
        "`!roast [@user]` - playful roast 🔥",
        "`!userinfo [@user]` - info about a user",
        "`!c or !cmd or !commands` - show this list",
    ]
    await ctx.send("\n".join(lines))


# ========= RUN THE BOT =========

bot.run(TOKEN)
