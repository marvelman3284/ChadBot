import discord, os, asyncio
from discord.ext import commands
from datetime import datetime, timedelta


# Helper methods
# Gets the user's roles, converts them to strings, and makes a comma seperated list out of them.
# Ignore @everyone if they have other roles
def role_list(user):
    roles = list(map(str, user.roles))
    if len(roles) != 1:
        roles.remove('@everyone')
    return ', '.join(roles)


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Information about the bot instance')
    async def info(self, ctx):
        commit = os.popen('git rev-parse --short HEAD').read().strip()
        embed = discord.Embed(
            title="Malcolm-Next",
            url="https://github.com/TheOtherUnknown/Malcolm-next")
        embed.add_field(name="Running Commit", value=commit,
                        inline=False)  # What commit is running?
        embed.add_field(name="Server count",
                        value=(len(self.bot.guilds)),
                        inline=False)
        embed.add_field(name="Owner", value=self.bot.owner_id, inline=False)
        await ctx.send(embed=embed)

    @commands.command(
        brief='Add yourself to the verified user role in the server, if you qualify')
    async def verify(self, ctx):
        joindate = ctx.author.joined_at
        if datetime.utcnow() > (joindate + timedelta(days=1)):  # One day
            await ctx.author.add_roles(
                discord.utils.get(ctx.guild.roles, name='Verified'))
            await ctx.message.add_reaction('✅')  # Check mark
        else:  # You didn't meet the time :(
            await ctx.send(
                'You don\'t qualify to be verified yet! Check back 24 hours after you join.'
            )

    @commands.command()
    async def ping(self, ctx):
        """Displays latency between client and bot"""
        latency = round(self.bot.latency * 1000, 2)
        return await ctx.send('Pong! ' + str(latency) + 'ms')

    @commands.command(brief='Displays information about the server')
    async def serverinfo(self, ctx):
        embed = discord.Embed(title=ctx.guild.name)
        if ctx.guild.description is not None:
            embed.description = ctx.guild.description
        embed.add_field(name='Region',
                        value=str(ctx.guild.region),
                        inline=True)
        embed.add_field(name='Members',
                        value=str(ctx.guild.member_count),
                        inline=True)
        embed.add_field(name='Owner', value=ctx.guild.owner.name, inline=True)
        cdate = ctx.guild.created_at
        embed.add_field(
            name='Creation date',
            value=f"{cdate.ctime()}, {(datetime.utcnow() - cdate).days} days ago")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"ID: {ctx.guild.id}")
        await ctx.send(embed=embed)

    @commands.command(brief='Displays information about users')
    async def userinfo(self, ctx, userid=None):
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif userid:
            user = ctx.guild.get_member(int(userid))
            if not user:
                await ctx.send("Cannot find user with that ID!")
                return
        else:
            user = ctx.author
        embed = discord.Embed(title=str(user))
        embed.set_thumbnail(url=user.avatar_url)
        create = f"{user.created_at.ctime()}, {(datetime.utcnow() - user.created_at).days} days ago"
        embed.add_field(name='Account created', value=create, inline=False)
        join = f"{user.joined_at.ctime()}, {(datetime.utcnow() - user.joined_at).days} days ago"
        embed.add_field(name="Join date", value=join, inline=False)
        embed.add_field(name="Roles", value=role_list(user), inline=False)
        embed.set_footer(text=f"ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.command(brief='Create polls using embeds and reactions',
                      usage="\"question\" \"answers 1-9\"")
    async def poll(self, ctx, question, *args):
        """
        Create embed polls with one question and up to 9 responses.
        """
        # Curernt max amount of answers is 9 as there are only 9 digit reactions

        if len(args) > 9:
            return await ctx.send(
                "You have provided more than nine choices; therefore, the poll was not sent"
            )

        reactions = [
            '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣'
        ]  # A list of all the reactions that could be added

        user = ctx.author  # Get the author for the footer of the embed

        embed = discord.Embed(
            title=f"**__{question}__**"
        )  # Set the title of the embed as the question provided
        embed.set_thumbnail(
            url=user.avatar_url
        )  # Set the thumbnail as the authors discord profile picture
        embed.set_author(
            name=user
        )  # Set the author of the embed as the person who sent the command

        for i, j in enumerate(args, 1):
            embed.add_field(name=str(i), value=str(j))

        msg = await ctx.send(embed=embed)

        for x in range(len(args)):
            await msg.add_reaction(reactions[x])

    # == START MOD COMMANDS == #

    @commands.command(brief='Bans a user from the server', usage='@someone')
    @commands.has_permissions(ban_members=True)
    async def kb(self, ctx):
        user = ctx.message.mentions[0]  # Get the first mentioned user
        await ctx.guild.ban(user, reason=f"Banned via command by {ctx.author}")

    @commands.command(brief="Kicks a mentioned user from the server",
                      usage="@someone")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx):
        if ctx.message.mentions[0] is not None:
            user = ctx.message.mentions[0]
            await ctx.guild.kick(user,
                                 reason=f"Kicked via command by {ctx.author}")

    @commands.command(brief='Mass-deletes messages in the current channel',
                      usage='<NUMBER>')
    @commands.has_permissions(manage_messages=True)
    async def nuke(self, ctx, num):
        if num is not None:
            num = int(
                num
            )  # Num can't be >100. That needs to be checked at some point
            async for message in ctx.channel.history(limit=num):
                message.delete()
            await asyncio.sleep(
                1.2)  # Sleep for a bit so everything gets deleted on time

    # == START OWNER COMMANDS == #
    @commands.command(hidden=True)
    @commands.is_owner()
    async def quit(self, ctx):
        await ctx.send('Malcolm is going down NOW!')
        raise SystemExit
