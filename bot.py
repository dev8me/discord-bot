import os
import random
import asyncio
import discord
from discord.ext import commands

# ========= CONFIG / TOKEN =========
# On Render: add env var ME = <your real bot token>
TOKEN = os.environ["ME"]

intents = discord.Intents.default()
intents.message_content = True  # make sure Message Content Intent is ON in dev portal

# disable default help so we can make our own commands list
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ========= MODERATION / TRACKING =========
BAD_WORDS = ["badword1", "badword2", "stupid"]  # change these if you want
spam_tracker = {}  # user_id -> (last_message, count)

# ========= XP / LEVEL SYSTEM =========
user_xp = {}      # user_id -> total XP
user_level = {}   # user_id -> current level


def get_level_from_xp(xp: int) -> int:
    # simple level formula: 50 XP per level
    return xp // 50


# ========= EVENTS =========

@bot.event
async def on_ready():
    print("Connected to Gateway")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")


@bot.event
async def on_message(message: discord.Message):
    # ignore our own bot messages
    if message.author == bot.user:
        return

    # ----- BAD WORD FILTER -----
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
        return

    # ----- SIMPLE SPAM CHECK -----
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

    # ----- XP / LEVEL SYSTEM -----
    if not message.author.bot and message.content.strip():
        gain = random.randint(5, 15)  # XP per message
        old_xp = user_xp.get(user_id, 0)
        new_xp = old_xp + gain
        user_xp[user_id] = new_xp

        old_level = user_level.get(user_id, 0)
        new_level = get_level_from_xp(new_xp)

        if new_level > old_level:
            user_level[user_id] = new_level
            await message.channel.send(
                f"🎉 GG {message.author.mention}! You leveled up to **level {new_level}**! 🚀"
            )

    # allow commands (!ping, etc.) to work
    await bot.process_commands(message)


# ========= BASIC COMMANDS =========

@bot.command()
async def ping(ctx: commands.Context):
    """Check if the bot is alive."""
    await ctx.send(f"Pong! 🏓 Latency: {round(bot.latency * 1000)} ms")


@bot.command()
async def slap(ctx: commands.Context, member: discord.Member = None):
    """Slap someone 👋"""
    if member is None:
        await ctx.send("Who do you want to slap? Use: `!slap @user`")
        return
    await ctx.send(f"{ctx.author.mention} slapped {member.mention} 💥")


@bot.command()
async def hug(ctx: commands.Context, member: discord.Member = None):
    """Give someone a hug 🤗"""
    if member is None:
        await ctx.send("Who do you want to hug? Use: `!hug @user`")
        return
    await ctx.send(f"{ctx.author.mention} gives {member.mention} a big hug 🤗💖")


# ========= MINI GAMES =========

@bot.command(name="coinflip", aliases=["cf", "coin"])
async def coinflip(ctx: commands.Context):
    """Flip a coin."""
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f"🪙 The coin landed on **{result}**!")


@bot.command(name="guess")
async def guess(ctx: commands.Context, number: int = None):
    """Guess a number between 1 and 10."""
    if number is None:
        await ctx.send("Use it like: `!guess 5` (number between 1 and 10)")
        return

    if number < 1 or number > 10:
        await ctx.send("Brooo pick a number **between 1 and 10** 😭")
        return

    bot_number = random.randint(1, 10)

    if number == bot_number:
        await ctx.send(f"🎉 GG {ctx.author.mention}! I picked **{bot_number}** too. You WIN!")
    else:
        await ctx.send(f"😔 L {ctx.author.mention}… I picked **{bot_number}**, not {number}.")


# ========= 8BALL / ROAST / USERINFO =========

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
]


@bot.command()
async def roast(ctx: commands.Context, member: discord.Member = None):
    """Playful roast 🔥 (don't be mean fr)"""
    if member is None:
        member = ctx.author

    roast_line = random.choice(ROASTS)
    await ctx.send(f"{member.mention} {roast_line}")


@bot.command()
async def userinfo(ctx: commands.Context, member: discord.Member = None):
    """Show info about a user."""
    if member is None:
        member = ctx.author

    embed = discord.Embed(
        title=f"User info: {member}",
        description=f"ID: {member.id}",
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    if member.joined_at:
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


# ========= LEVEL COMMANDS =========

@bot.command(name="level", aliases=["rank"])
async def level_cmd(ctx: commands.Context, member: discord.Member = None):
    """Show your level and XP."""
    if member is None:
        member = ctx.author

    uid = member.id
    xp = user_xp.get(uid, 0)
    level = user_level.get(uid, get_level_from_xp(xp))
    next_level_xp = (level + 1) * 50

    await ctx.send(
        f"📊 {member.mention} — Level **{level}**, XP **{xp}/{next_level_xp}**"
    )


@bot.command(name="leaderboard", aliases=["lb", "top"])
async def leaderboard(ctx: commands.Context):
    """Show top 5 users by XP."""
    if not user_xp:
        await ctx.send("Nobody has XP yet 😭 start chatting first.")
        return

    sorted_users = sorted(user_xp.items(), key=lambda x: x[1], reverse=True)

    lines = []
    place = 1
    for user_id, xp in sorted_users[:5]:
        member = ctx.guild.get_member(user_id)
        if member is None:
            continue
        level = user_level.get(user_id, get_level_from_xp(xp))
        lines.append(
            f"**#{place}** {member.mention} — Level **{level}**, XP **{xp}**"
        )
        place += 1

    if not lines:
        await ctx.send("Nobody on the leaderboard yet 😭")
    else:
        await ctx.send("🏆 **XP Leaderboard** 🏆\n" + "\n".join(lines))


# ========= COMMAND LIST =========

@bot.command(name="commands")
async def commands_list(ctx: commands.Context):
    """Show all commands for this bot."""
    lines = [
        "**Here are my commands:**",
        "`!ping` - check if the bot is alive",
        "`!slap @user` - slap someone 💥",
        "`!hug @user` - give someone a hug 🤗",
        "`!coinflip` / `!cf` / `!coin` - flip a coin 🪙",
        "`!guess <1-10>` - guess the number 🔢",
        "`!8ball <question>` - magic 8ball 🎱",
        "`!roast [@user]` - playful roast 🔥",
        "`!userinfo [@user]` - info about a user",
        "`!level` / `!rank` - show your level and XP",
        "`!leaderboard` / `!lb` / `!top` - top 5 by XP",
        "`!commands` - show this list",
    ]
    await ctx.send("\n".join(lines))


# ========= RUN THE BOT ==========
bot.run(TOKEN)
