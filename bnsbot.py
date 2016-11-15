import discord
import asyncio
import json
import pickle
import os
import bns.characters
import config

client = discord.Client()

class ClanState(object):
    def __init__(self):
        self._clan_members = []
        self._clan_name = ""

    def add_member(self, member_ign):
        self._clan_members.append(member_ign)

    def remove_member(self, member_ign):
        self._clan_members.remove(member_ign)

    def save_clan_state(self):
        with open("clan_state.pkl", "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load_clan_state():
        if os.path.exists("clan_state.pkl"):
            with open("clan_state.pkl", "rb") as f:
                return pickle.load(f)
        else:
            return ClanState()

    def get_clan_members(self):
        return self._clan_members

    def get_clan_name(self):
        return self._clan_name

    def set_clan_name(self, clan_name):
        self._clan_name = clan_name


clan_state = ClanState.load_clan_state()


class PermissionDeniedException(Exception):
    pass


def check_permissions(user):
    if all(user.id != x for x in config.bot_owner):
        raise PermissionDeniedException()


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




def get_members_list_str(members):
    result = ""
    for ign, info in members.items():
        if info:
            result += "{}: {}".format(ign, json.dumps(info)) + "\n"
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
        member_ign = member
        print("Calculating for member {}".format(member_ign))
        info = await bns.characters.get_character_info(member_ign)
        members_info[member_ign] = info
        i += 1
        if i > 10:
            await client.send_message(channel, '```\n{}\n```'.format(get_members_list_str(members_info)))
            members_info = {}
            i = 0

    print("Done retrieving information")


def format_member_info(ign, info):
    return """{}:
AP: {}
crit: {}
cdmg: {}
piercing: {}
accuracy: {}
necklace: {}""".format(ign, info["AP"], info["crit"], info["cdmg"], info["piercing"], info["accuracy"], "Stage {}".format(info["neck_stage"]) if info["neck_stage"] else "-----")


async def print_single_member(channel, member_ign):
    tmp = await client.send_message(channel, 'Calculating info...')
    info = await bns.characters.get_character_info(member_ign)
    await client.edit_message(tmp, '```\n{}\n```'.format(format_member_info(member_ign, info)))


def check_if_command(str, command):
    return str == command or str.startswith(command + " ")


@client.event
async def on_message(message):
    # TODO add help command
    try:
        if check_if_command(message.content, "!get_member_stats"):
            command_parts = message.content.split(" ")
            if len(command_parts) == 1:
                await print_all_members(message.channel, clan_state.get_clan_members())
            elif len(command_parts) >= 2:
                member_ign =  " ".join(command_parts[1:])
                print("Retrieving info for {}".format(member_ign))
                await print_single_member(message.channel, member_ign)

        elif check_if_command(message.content, "!get_user_id"):
            await client.send_message(message.channel, message.author.id)
        elif check_if_command(message.content, "!create_clan_members_list_from_server"):
            check_permissions(message.author)
            print("Recording current clan members")
            for member in message.channel.server.members:
                clan_state.add_member(get_nickname(member))
            clan_state.save_clan_state()

            await client.send_message(message.channel, "Done.")

        elif check_if_command(message.content, "!print_members"):
            results = ""
            for member in clan_state.get_clan_members():
                results += member + "\n"

            await client.send_message(message.channel, "```\n{}\n```".format(results))
        elif check_if_command(message.content, "!set_clan_name"):
            check_permissions(message.author)
            command_parts = message.content.split(" ")
            clan_state.set_clan_name(" ".join(command_parts[1:]))
            clan_state.save_clan_state()
            await client.send_message(message.channel, "Done.")
        elif check_if_command(message.content, "!get_clan_name"):
            await client.send_message(message.channel, clan_state.get_clan_name())
        elif check_if_command(message.content, "!who_left_clan"):
            print("Checking who left clan")
            results = ""
            for member_ign in clan_state.get_clan_members():
                info = await bns.characters.get_character_info(member_ign)
                if not info or info["guild"] != clan_state.get_clan_name():
                    results += member_ign + "\n"
                    print(member_ign)
            await client.send_message(message.channel, "```\n{}\n```".format(results))
        elif check_if_command(message.content, "!remove_member"):
            check_permissions(message.author)
            command_parts = message.content.split(" ")
            try:
                clan_state.remove_member(" ".join(command_parts[1:]))
                clan_state.save_clan_state()
                await client.send_message(message.channel, "Removed member")
            except ValueError:
                await client.send_message(message.channel, "Member name does not exists")

        elif check_if_command(message.content, "!add_member"):
            check_permissions(message.author)
            command_parts = message.content.split(" ")
            clan_state.add_member(" ".join(command_parts[1:]))
            clan_state.save_clan_state()
            await client.send_message(message.channel, "Done.")
        elif check_if_command(message.content, "!check_legendary_necklace"):
            results = ""
            for member in clan_state.get_clan_members():
                print("Checking " + member + " for necklace")
                info = await bns.characters.get_character_info(member)
                if info and not info["neck_stage"]:
                    print(member + " Doesnt have necklace")
                    results += member + "\n"

            await client.send_message(message.channel, "```\nMembers who doesnt have legendary necklace:\n{}\n```".format(results))
        elif check_if_command(message.content, "!sleep"):
            await asyncio.sleep(5)
            await client.send_message(message.channel, "Done sleeping")
    except PermissionDeniedException as e:
        print("Permission Denied")
        await client.send_message(message.channel, "Permission Denied")


client.run(config.token)