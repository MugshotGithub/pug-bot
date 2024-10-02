import json
import os
import sqlite3

import discord
from discord import app_commands
from dotenv import dotenv_values

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Get env values, quit if incorrectly configured
if os.path.exists(".env"):
    config = dotenv_values(".env")
else:
    print(".env not found")
    quit(1)


bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
guildId = int(config["GUILD_ID"])

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guildId))
    print(f'Logged in as {bot.user.name}')
    print('------')


async def _isAdmin(userId):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admins WHERE id = (?) ;', (userId,))
    memberFound = cursor.fetchall()

    cursor.execute('SELECT * FROM admins WHERE type = "role"')
    roleIds = cursor.fetchall()

    conn.close()

    if len(memberFound) > 1:
        return True

    guild = bot.get_guild(guildId) if bot.get_guild(guildId) is not None else await bot.fetch_guild(guildId)
    member = guild.get_member(userId) if guild.get_member(userId) is not None else await guild.fetch_member(userId)

    if member.guild_permissions.administrator:
        return True
    print(roleIds)
    memberRoleIds = [role.id for role in member.roles]

    for memberRoleId in memberRoleIds:
        if memberRoleId in roleIds:
            return True

    return False

@tree.command(name="setup-pugs", description="Initialised all channels for PUG lobbies",guild=discord.Object(id=guildId))
async def setup_pug(interaction):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return
    guild = bot.get_guild(guildId) if bot.get_guild(guildId) is not None else await bot.fetch_guild(guildId)

    category = await guild.create_category("pugs")

    signUpChannel = await category.create_text_channel("sign-up")

    await signUpChannel.set_permissions(guild.default_role, read_messages=True, send_messages=False)
    await signUpChannel.set_permissions(guild.get_member(bot.user.id), read_messages=True, send_messages=False)

    discussionChannel = await category.create_text_channel("pug-discussion")

    if not os.path.exists("lobbyData.json"):
        with open("lobbyData.json.txt", "w") as file:
            file.write("{}")

    # TODO: Send sign up message HERE

    lobbyChannel = await category.create_voice_channel("Lobby")
    redTeamChannel = await category.create_voice_channel("Red Team")
    blueTeamChannel = await category.create_voice_channel("Blue Team")
    channelIds = {
        "signUp": signUpChannel.id,
        "discussion": discussionChannel.id,
        "lobby": lobbyChannel.id,
        "red": redTeamChannel.id,
        "blue": blueTeamChannel.id
    }





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

    conn = sqlite3.connect('database.db', autocommit=True)
    cursor = conn.cursor()

    cursor.execute('INSERT OR IGNORE INTO admins (id,type) VALUES (?,"user");', (member.id,))

    conn.close()

    await interaction.followup.send(f"Added {member.display_name} to the admin list")


@tree.command(name="remove-admin-user", description="Removes a member from the list of admins",
              guild=discord.Object(id=guildId))
async def remove_admin_user(interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    conn = sqlite3.connect('database.db', autocommit=True)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM admins WHERE id = ?;', (member.id,))

    conn.close()

    await interaction.followup.send(f"Removed {member.display_name} from the admin list")


@tree.command(name="add-admin-role", description="Adds a role to the list of roles that count as admins",
              guild=discord.Object(id=guildId))
async def add_admin_role(interaction, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    conn = sqlite3.connect('database.db', autocommit=True)
    cursor = conn.cursor()

    cursor.execute('INSERT OR IGNORE INTO admins (id,type) VALUES (?,"role");', (role.id,))

    conn.close()

    await interaction.followup.send(f"Added {role.name} to the admin list")


@tree.command(name="remove-admin-role", description="Removes a role to the list from roles that count as admins",
              guild=discord.Object(id=guildId))
async def remove_admin_role(interaction, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    conn = sqlite3.connect('database.db', autocommit=True)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM admins WHERE id = ?;', (role.id,))

    conn.close()

    await interaction.followup.send(f"Removed {role.name} from the admin list")

@tree.command(name="clear-admin-list", description="Clears entire admin list",
              guild=discord.Object(id=guildId))
async def clear_admin_list(interaction):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    conn = sqlite3.connect('database.db', autocommit=True)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM admins;')

    conn.close()

    await interaction.followup.send(f"Cleared the admin list")

@tree.command(name="list-admin-users", description="Lists current admin users",
              guild=discord.Object(id=guildId))
async def see_admin_users(interaction):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    guild = bot.get_guild(guildId) if bot.get_guild(guildId) is not None else await bot.fetch_guild(guildId)

    conn = sqlite3.connect('database.db', autocommit=True)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM admins WHERE type == "user";')
    memberIds = cursor.fetchall()
    conn.close()

    members = "Admin members:"
    for memberId in memberIds:
        memberId = memberId[0]
        member = guild.get_member(memberId) if guild.get_member(memberId) is not None else await guild.fetch_member(memberId)
        members += f"\n{member.name}"

    await interaction.followup.send(members)

@tree.command(name="list-admin-roles", description="Lists roles on the admin list",
              guild=discord.Object(id=guildId))
async def see_admin_roles(interaction):
    await interaction.response.defer(ephemeral=True)
    if not await _isAdmin(interaction.user.id):
        await interaction.followup.send(f"You do not have permission to use this command")
        return

    guild = bot.get_guild(guildId) if bot.get_guild(guildId) is not None else await bot.fetch_guild(guildId)

    conn = sqlite3.connect('database.db', autocommit=True)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM admins WHERE type == "role";')
    roleIds = cursor.fetchall()

    conn.close()

    roles = "Admin roles:"
    for roleId in roleIds:
        roleId = roleId[0]
        role = guild.get_role(roleId)
        roles += f"\n{role.name}"

    await interaction.followup.send(roles)

bot.run(config["BOT_KEY"])
