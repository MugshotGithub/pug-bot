import json
import os

import discord
from discord import app_commands
from dotenv import dotenv_values

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
guildId = int(os.getenv("GUILD_ID"))

# Get env values, quit if incorrectly configured
if os.path.exists(".env"):
    config = dotenv_values(".env")
else:
    print(".env not found")
    quit(1)


async def on_ready():
    await tree.sync(guild=discord.Object(id=guildId))
    print(f'Logged in as {bot.user.name}')
    print('------')


async def _isAdmin(userId):
    adminFile = open("admins.json")
    adminData = json.load(adminFile)
    adminFile.close()

    guild = bot.get_guild(guildId) if bot.get_guild(guildId) is not None else await bot.fetch_guild(guildId)
    member = guild.get_member(userId) if guild.get_member(userId) is not None else await guild.fetch_member(userId)

    if member.guild_permissions.administrator:
        return True

    for adminId in adminData["users"]:
        if userId == adminId:
            return True

    roleIds = [role.id for role in member.roles]

    for roleId in adminData["roles"]:
        if roleId in roleIds:
            return True

    return False

#########################################################
# This bot uses an internal admin system. Users with Admin permissions from the server are also granted these permissions
#########################################################
@tree.command(name="add-admin-user", description="Adds a member to the list of admins",
              guild=discord.Object(id=guildId))
async def add_admin_user(interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    if os.path.exists("lobbyData.json"):
        guild = bot.get_guild(guildId) if bot.get_guild(guildId) is not None else await bot.fetch_guild(guildId)
        with open("lobbyData.json") as data:
            jsonData = json.load(data)
            channel = guild.get_channel(jsonData["auditId"]) if guild.get_channel(jsonData["auditId"]) is not None else await guild.fetch_channel(jsonData["auditId"])
            await channel.set_permissions(member, read_messages=True)

    adminFile = open("admins.json")
    adminData = json.load(adminFile)

    adminData["users"].append(member.id)
    adminFile.close()

    adminFile = open("admins.json", "w")
    json.dump(adminData, adminFile)
    adminFile.close()

    await interaction.followup.send(f"Added {member.display_name} to the admin list")


@tree.command(name="remove-admin-user", description="Removes a member from the list of admins",
              guild=discord.Object(id=guildId))
async def remove_admin_user(interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    if os.path.exists("lobbyData.json"):
        guild = bot.get_guild(guildId) if bot.get_guild(guildId) is not None else await bot.fetch_guild(guildId)
        with open("lobbyData.json") as data:
            jsonData = json.load(data)
            channel = guild.get_channel(jsonData["auditId"]) if guild.get_channel(jsonData["auditId"]) is not None else await guild.fetch_channel(jsonData["auditId"])
            await channel.set_permissions(member, read_messages=False)

    adminFile = open("admins.json")
    adminData = json.load(adminFile)

    try:
        adminData["users"].remove(member.id)
    except ValueError:
        pass

    adminFile.close()
    adminFile = open("admins.json", "w")
    json.dump(adminData, adminFile)
    adminFile.close()

    await interaction.followup.send(f"Removed {member.display_name} from the admin list")


@tree.command(name="add-admin-role", description="Adds a role to the list of roles that count as admins",
              guild=discord.Object(id=guildId))
async def add_admin_role(interaction, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    if os.path.exists("lobbyData.json"):
        guild = bot.get_guild(guildId) if bot.get_guild(guildId) is not None else await bot.fetch_guild(guildId)
        with open("lobbyData.json") as data:
            jsonData = json.load(data)
            channel = guild.get_channel(jsonData["auditId"]) if guild.get_channel(jsonData["auditId"]) is not None else await guild.fetch_channel(jsonData["auditId"])
            await channel.set_permissions(role, read_messages=True)

    adminFile = open("admins.json")
    adminData = json.load(adminFile)

    adminData["roles"].append(role.id)

    adminFile.close()
    adminFile = open("admins.json", "w")
    json.dump(adminData, adminFile)
    adminFile.close()

    await interaction.followup.send(f"Added {role.name} to the admin list")


@tree.command(name="remove-admin-role", description="Removes a role to the list from roles that count as admins",
              guild=discord.Object(id=guildId))
async def remove_admin_role(interaction, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    if os.path.exists("lobbyData.json"):
        guild = bot.get_guild(guildId) if bot.get_guild(guildId) is not None else await bot.fetch_guild(guildId)
        with open("lobbyData.json") as data:
            jsonData = json.load(data)
            channel = guild.get_channel(jsonData["auditId"]) if guild.get_channel(jsonData["auditId"]) is not None else await guild.fetch_channel(jsonData["auditId"])
            await channel.set_permissions(role, read_messages=False)

    adminFile = open("admins.json")
    adminData = json.load(adminFile)

    try:
        adminData["roles"].remove(role.id)
    except ValueError:
        pass

    adminFile.close()
    adminFile = open("admins.json", "w")
    json.dump(adminData, adminFile)
    adminFile.close()

    await interaction.followup.send(f"Removed {role.name} from the admin list")

bot.run(config["BOT_KEY"])
