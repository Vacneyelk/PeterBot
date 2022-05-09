import shlex
from typing import TYPE_CHECKING, List

import aiohttp
import discord
from cogs.custom_ui.page_turn_embed import PageTurnView
from discord.ext import commands

if TYPE_CHECKING:
    from peterbot import PeterBot


class Schedule(commands.Cog):
    """Handler for associated UCI Schedule commands

    Parameters
    ----------
    bot : PeterBot
        The bot object

    Commands
    ----------
    soc : Searches PeterPortal API for SOC
    """

    def __init__(self, bot: "PeterBot"):
        self.bot = bot

    @commands.command(
        name="soc",
        brief="Search UCI SOC",
        usage="soc [term] [flags]",
        example="soc 2020 Fall --ge GE-1A",
        help="Search for classes on the UCI SOC",
        description="""
        Flags:
        --ge:               [ANY, GE-1A, GE-3,...]*
        --department:       Dept. names. Ex: I&C SCI, PSYC*
        --courseNumber      [32A, 31-33,]*
        --division          [ALL, LowerDiv, UpperDiv, Graduate]
        --sectionCodes      WebReg codes. Ex: 44201*
        --instructorName    Instructor last name. Ex: Holton*
        --courseTitle       Course name. Ex: Intro to Chem
        --sectionType       [ALL, LEC, LAB, SEM, ...]
        --units             Integer OR 'VAR' for variable
        --days              [M, T, W, Th, F, MWF, ...]
        --startTime         12hr formatted time. Ex: 1:00PM
        --endTime           12hr formatted time. Ex: 2:00PM
        --maxCapacity       Integer, < and > optional. Ex: <300
        --fullCourses       [ANY, SkipFullWaitlist, FullOnly, OverEnrolled]
        --cancelledCourses  [Exclude, Include, Only]
        --building          Building codes. Ex: EH
        --room              Room number. Ex: 1200

        * = one of these required
        """,
    )
    async def soc(self, ctx: "commands.Context", *args):
        """Command to search PeterPortal API for SOC"""

        # Parse arg string into term string and flag dict
        # Ex:
        #       "2022 Spring --ge GE-4 --department CHEM"
        #   becomes
        #       term = "2022 Spring"
        #       flags = {"ge":"GE-4", "department":"CHEM"}
        message = await ctx.send("Searching")
        term = " ".join(args).split("--")[0]
        flags = shlex.split(" ".join(args[2:]))
        flags = dict(zip([f.replace("--", "") for f in flags[::2]], flags[1::2]))

        # Check command for potential errors, like missing mandatory flags
        if not any(
            [st in term.lower() for st in ["spring", "summer", "fall", "winter"]]
        ):
            await ctx.send("Missing term. See `$help soc` on how to structure command.")
            return

        if not any(
            f in flags.keys()
            for f in [
                "department",
                "ge",
                "courseCodes",
                "sectionCodes",
                "instructorName",
            ]
        ):
            await ctx.send(
                "Missing one of: ['department', 'ge', 'courseNumber', 'sectionCodes', 'instructorName']"
            )
            return

        # Search the PeterPortalAPI
        search: List["Course"] = await PeterPortalAPI(term=term, **flags)

        # Handle 0 results
        if len(search) == 0:
            await ctx.send(
                "No results found. Please try again with different search terms."
            )

        # Handle case where user is looking for a specific section
        embeds: List["discord.Embed"] = []
        if "sectionCodes" in flags.keys():
            c = search[0]
            await c.detail()
            c = c.sections[0]

            if c.sectionCode:
                embeds.append(
                    discord.Embed(
                        title=f"{search[0].id} ({c.sectionCode}) - {c.sectionType}",
                        description=search[0].description,
                    )
                )

            if c.instructors:
                embeds[0].add_field(name="Instructors", value="\n".join(c.instructors))

            if c.meetings:
                embeds[0].add_field(
                    name="Meetings",
                    value="\n".join(
                        [f"{m['days']}, {m['time']} @ {m['bldg']}" for m in c.meetings]
                    ),
                )

            if c.status:
                embeds[0].add_field(name="Status", value=c.status)

            if c.numCurrentlyEnrolled:
                embeds[0].add_field(
                    name="Currently Enrolled",
                    value="\n".join(
                        [
                            f"Total Enrolled: {c.numCurrentlyEnrolled['totalEnrolled']}",
                            f"Section Enrolled: {c.numCurrentlyEnrolled['sectionEnrolled'] if c.numCurrentlyEnrolled['sectionEnrolled'] != '' else 'n/a'}",
                        ]
                    ),
                )

            if c.numOnWaitlist:
                embeds[0].add_field(name="Waitlist", value=c.numOnWaitlist)

            if c.restrictions:
                embeds[0].add_field(name="Restrictions", value=c.restrictions)

        # Default case
        else:

            # Format the results into discord Embeds
            if len(search) > 10:
                search = search[:10]

            for c in search:
                await c.detail()
                embed = discord.Embed(title=c.id, description=c.description)

                if c.units:
                    embed.add_field(name="Units", value=str(c.units))

                if c.ge_text:
                    embed.add_field(name="GE", value=c.ge_text)

                if c.overlap:
                    embed.add_field(name="Overlap", value=c.overlap)

                if len(c.terms) > 10:
                    c.terms = c.terms[:10]
                embed.add_field(name="Past Terms", value=", ".join(c.terms))

                if len(c.sections) > 10:
                    c.sections = c.sections[:10]

                embed.add_field(
                    name="Sections",
                    value=", ".join([str(s.sectionCode) for s in c.sections]),
                )
                embeds.append(embed)

        # Multiple Page result display
        current_page = 0
        await message.edit(
            content="",
            embed=embeds[current_page % len(embeds)],
            view=PageTurnView(ctx, embeds, message),
        )
        return


class PeterPortalAPI:
    """Asynchronous wrapper for the PeterPortal API.

    Provides SOC and Course lookup functionality

    See https://api.peterportal.org/docs/REST-API/schedule/
    for parameter documentation.
    """

    def __init__(self, term: str = None, **kwargs: str):
        self.term = term
        self.kwargs = kwargs

    def __await__(self) -> List["Course"]:
        async def search():

            # Malformed search checking
            if self.term is None:
                raise ValueError("Class term must be specified")

            # Formatting for URL string
            self.term = self.term.replace(" ", "%20")
            for key, val in self.kwargs.items():
                self.kwargs[key] = val.replace(" ", "%20")
                self.kwargs[key] = val.replace("&", "%26")
                self.kwargs[key] = val.replace("/", "%2F")
            parameters = "&" + "&".join(
                [f"{key}={value}" for key, value in self.kwargs.items()]
            )
            url = f"https://api.peterportal.org/rest/v0/schedule/soc?term={self.term}{parameters}"

            # API call to PeterPortal
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise
                    apiResp = await resp.json()

            # Creating list of Course() objects from API response
            returnList = []
            for school in apiResp["schools"]:
                for dept in school["departments"]:
                    for course in dept["courses"]:
                        returnList.append(
                            Course(
                                id=course["deptCode"] + course["courseNumber"],
                                department=course["deptCode"],
                                number=course["courseNumber"],
                                title=course["courseTitle"],
                                courseComment=course["courseComment"],
                                prerequisiteURL=course["prerequisiteLink"],
                                sections=course["sections"],
                            )
                        )
            return returnList

        return search().__await__()


class Course:
    """General UCI Course object.
    See https://api.peterportal.org/REST-API/schedule/ for information the API provides

    Methods
    ----------
    detail() -> None:
        Calls another PeterPortal API for additional course information.
        See https://api.peterportal.org/REST-API/courses/ for information the API provides.
    """

    def __init__(self, **kwargs) -> None:

        # Set Course() object attributes
        for k, v in kwargs.items():
            setattr(self, k, v)

        # Creates list of Section() objects
        self.sections = []
        try:
            for sec in kwargs["sections"]:
                self.sections.append(Section(**sec))
        except Exception:
            pass

    async def detail(self) -> None:
        """Adds additional course details to a Course() object

        See https://api.peterportal.org/REST-API/courses/ for information the API provides.
        """
        # API call to PeterPortal
        url = f"https://api.peterportal.org/rest/v0/courses/{self.id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise
                apiResp = await resp.json()

        # Add additional attributes to existing Course() object
        for k, v in apiResp.items():
            setattr(self, k, v)

        return


class Section(Course):
    """One section of a specific UCI Course.
    Inherits from Course class, adds additional information specific to a section.

    See https://api.peterportal.org/docs/REST-API/schedule/ for information the API provides
    (contained within sections list)
    """

    def __init__(self, **kwargs) -> None:

        # Set Section() object attributes
        for k, v in kwargs.items():
            setattr(self, k, v)


async def setup(bot: "PeterBot") -> None:
    await bot.add_cog(Schedule(bot))
