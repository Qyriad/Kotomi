#!/usr/bin/env python3

# Kurisu by 916253 & ihaveamac
# license: Apache License 2.0
# https://github.com/916253/Kurisu

description = """
Homura, the moderation bot of Room of Requirement.
"""

# import dependencies
import os
from discord.ext import commands
import discord
import datetime
import json, asyncio
import copy
import configparser
import traceback
import sys
import os

# sets working directory to bot's folder
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# read config for token
config = configparser.ConfigParser()
config.read("config.ini")

os.makedirs("data", exist_ok=True)
# create warnsv2.json if it doesn't exist, and convert warns.json if needed
if not os.path.isfile("data/warnsv2.json"):
    if os.path.isfile("data/warns.json"):
        print("Converting warns.json to warnsv2 format")
        with open("data/warns.json", "r") as f:
            warns = json.load(f)
        warnsv2 = {}
        for user_id, info in warns.items():
            warnsv2[user_id] = {"name": info["name"], "warns": []}
            for w_idx in range(len(info["warns"])):
                warnsv2[user_id]["warns"].append(info["warns"][str(w_idx + 1)])
        with open("data/warnsv2.json", "w") as f:
            json.dump(warnsv2, f)
    else:
        with open("data/warnsv2.json", "w") as f:
            f.write("{}")

# create restrictions.json if it doesn't exist
if not os.path.isfile("data/restrictions.json"):
    with open("data/restrictions.json", "w") as f:
        f.write("{}")


# create helpers.json if it doesn't exist
if not os.path.isfile("data/helpers.json"):
    with open("data/helpers.json", "w") as f:
        f.write("{}")

# create timebans.json if it doesn't exist
if not os.path.isfile("data/timebans.json"):
    with open("data/timebans.json", "w") as f:
        f.write("{}")


prefix = ['!']
bot = commands.Bot(command_prefix=prefix, description=description, pm_help=None)

bot.actions = []  # changes messages in mod-/server-logs

# http://stackoverflow.com/questions/3411771/multiple-character-replace-with-python
chars = "\\`*_<>#@:~"
def escape_name(name):
    name = str(name)
    for c in chars:
        if c in name:
            name = name.replace(c, "\\" + c)
    return name.replace("@", "@\u200b")  # prevent mentions
bot.escape_name = escape_name

bot.pruning = False  # used to disable leave logs if pruning, maybe.

# mostly taken from https://github.com/Rapptz/discord.py/blob/async/discord/ext/commands/bot.py
@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        pass  # ...don't need to know if commands don't exist
    if isinstance(error, discord.ext.commands.errors.CheckFailure):
        await bot.send_message(ctx.message.channel, "{} You don't have permission to use this command.".format(ctx.message.author.mention))
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        formatter = commands.formatter.HelpFormatter()
        await bot.send_message(ctx.message.channel, "{} You are missing required arguments.\n{}".format(ctx.message.author.mention, formatter.format_help_for(ctx, ctx.command)[0]))
    else:
        if ctx.command:
            await bot.send_message(ctx.message.channel, "An error occured while processing the `{}` command.".format(ctx.command.name))
        print('Ignoring exception in command {}'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

bot.all_ready = False
bot._is_all_ready = asyncio.Event(loop=bot.loop)
async def wait_until_all_ready():
    """Wait until the entire bot is ready."""
    await bot._is_all_ready.wait()
bot.wait_until_all_ready = wait_until_all_ready

@bot.event
async def on_ready():
    if bot.all_ready:
        return
    # this bot should only ever be in one server anyway
    for server in bot.servers:
        print("{} has started! {} has {:,} members!".format(bot.user.name, server.name, server.member_count))
        bot.server = server

        bot.config = config

        # channels
        bot.mods_channel = discord.utils.get(server.channels, name="server-logs")
        bot.modlogs_channel = discord.utils.get(server.channels, name="server-logs")
        bot.serverlogs_channel = discord.utils.get(server.channels, name="server-logs")
        bot.messagelogs_channel = discord.utils.get(server.channels, name="server-logs")
        bot.welcome_channel = discord.utils.get(server.channels, name="entry-gate")

        # TODO: remove some of these roles that are useless on Reswitched. need to find their use around the bot first.
        # roles
        bot.staff_role = discord.utils.get(server.roles, name="Mod")
        bot.verified_role = discord.utils.get(server.roles, name="vetted")
        bot.muted_role = discord.utils.get(server.roles, name="Muted")
        bot.everyone_role = server.default_role

        bot.she_her_role = discord.utils.get(server.roles, name="she/her")
        bot.they_them_role = discord.utils.get(server.roles, name="they/them")
        bot.he_him_role = discord.utils.get(server.roles, name="he/him")
        bot.girl_role = discord.utils.get(server.roles, name="girl")
        bot.boy_role = discord.utils.get(server.roles, name="boy")
        bot.non_binary_role = discord.utils.get(server.roles, name="non-binary")
        bot.straight_role = discord.utils.get(server.roles, name="straight")
        bot.gay_role = discord.utils.get(server.roles, name="gay")
        bot.bi_pan_role = discord.utils.get(server.roles, name="bi/pan")
        bot.ace_role = discord.utils.get(server.roles, name="ace")
        bot.aro_role = discord.utils.get(server.roles, name="aro")
        bot.cis_role = discord.utils.get(server.roles, name="cis")
        bot.trans_role = discord.utils.get(server.roles, name="trans")

        bot.extra_roles = [bot.she_her_role, bot.they_them_role, bot.he_him_role, bot.girl_role, bot.boy_role, bot.non_binary_role, bot.straight_role, bot.gay_role, bot.bi_pan_role, bot.ace_role, bot.aro_role, bot.cis_role, bot.trans_role]

        bot.nsfw_role = discord.utils.get(server.roles, name="bad dragon")

        # load timebans
        with open("data/timebans.json", "r") as f:
            timebans = json.load(f)
        bot.timebans = {}
        timebans_i = copy.copy(timebans)
        for user_id, timestamp in timebans_i.items():
            found = False
            for user in await bot.get_bans(server):
                if user.id == user_id:
                    bot.timebans[user_id] = [user, datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"), False]  # last variable is "notified", for <=30 minute notifications
                    found = True
                    break
            if not found:
                timebans.pop(user_id) # somehow not in the banned list anymore so let's just remove it
        with open("data/timebans.json", "w") as f:
            json.dump(timebans, f)

        bot.all_ready = True
        bot._is_all_ready.set()

        msg = "{} has started! {} has {:,} members!".format(bot.user.name, server.name, server.member_count)
        if len(failed_addons) != 0:
            msg += "\n\nSome addons failed to load:\n"
            for f in failed_addons:
                msg += "\n{}: `{}: {}`".format(*f)
        await bot.send_message(bot.serverlogs_channel, msg)


        break

# loads extensions
addons = [
    'addons.blah',
    'addons.extras',
    'addons.kickban',
    'addons.load',
    'addons.lockdown',
    'addons.logs',
    'addons.mod',
    'addons.mod_warn',
]

failed_addons = []

for extension in addons:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print('{} failed to load.\n{}: {}'.format(extension, type(e).__name__, e))
        failed_addons.append([extension, type(e).__name__, e])

# Execute
print('Bot directory: ', dir_path)
bot.run(config['Main']['token'])
