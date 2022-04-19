import discord
from discord.ext import commands
from peterbot import PeterBot


class Utilities(commands.Cog):
    def __init__(self, bot: PeterBot):
        self.bot = bot

    @commands.command()
    async def user(self, ctx: commands.Context, snowflake: int):
        """ """
        user = await self.bot.get_user(int(snowflake))
        if user is None:
            await ctx.send(f"A user for snowflake={snowflake} could not be found")
        embed = discord.Embed(title=f"Snowflake: {snowflake}", color=2097148)
        embed.add_field(
            name="Discord Id", value=f"{user.name}#{user.discriminator}", inline=False
        )
        embed.add_field(name="Creation Date", value=f"{user.created_at}", inline=False)
        embed.add_field(name="Avatar URL", value=f"{user.avatar_url}")
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utilities(bot))
