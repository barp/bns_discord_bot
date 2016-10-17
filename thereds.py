import discord
import asyncio
import json
import bns.characters

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('---------')

def get_nickname(member):
    if member.nick:
        return member.nick
    else:
        return str(member).split("#")[0]

def format_member_info(ign, info):
    # TODO better font formatting to messages
    return "{}: {}".format(ign, json.dumps(info))

def get_members_list_str(members):
    result = ""
    for ign, info in members.items():
        if info:
            result += format_member_info(ign, info) + "\n"
        else:
            result += "{}: Information does not exist\n".format(ign)

    return result


@client.event
async def on_member_join(member):
    pass

@client.event
async def on_member_remove(member):
    pass

async def print_all_members(channel, members):
    tmp = await client.send_message(channel, 'Calculating info...')

    members_info = {}

    i = 0

    for member in members:
        member_ign = get_nickname(member)
        print("Calculating for member {}".format(member_ign))
        info = await bns.characters.get_character_info(member_ign)
        members_info[member_ign] = info
        i += 1
        if i > 10:
            await client.send_message(channel, '```\n{}\n```'.format(get_members_list_str(members_info)))
            members_info = {}
            i = 0

    print("Done retrieving information")

@client.event
async def on_message(message):
    # TODO add help command
    if message.content.startswith("!get_member_stats"):
        command_parts = message.content.split(" ")
        if len(command_parts) == 1:
            await print_all_members(message.channel, message.channel.server.members)
        elif len(command_parts) >= 2:
            member_ign = " ".join(command_parts[1:])
            tmp = await client.send_message(message.channel, 'Calculating info...')
            info = await bns.characters.get_character_info(member_ign)
            await client.edit_message(tmp, '```\n{}\n```'.format(format_member_info(member_ign, info)))

    elif message.content.startswith("!sleep"):
        await asyncio.sleep(5)
        await client.send_message(message.channel, "Done sleeping")


client.run("MjM3MTI5MjM3NDc4Mzc1NDI1.CuTL5A.G6st2BQXWB3IlXG4cv5AdUuKqaY")