import asyncio
import aiohttp
from urllib.parse import quote
from bs4 import BeautifulSoup as Soup
from soupselect import select
import collections

def get_info_from_title(soup, name):
    stats = select(soup, "dt.stat-title")

    for stat in stats:

        stat_name = select(stat, "span.title")
        if stat_name:
            if stat_name[0].text == name:
                return select(stat, "span.stat-point")[0].text

def get_ap(soup):
    return get_info_from_title(soup, "Attack Power")

def get_piercing(soup):
    return get_info_from_title(soup, "Piercing")


def get_info_from_description(soup, desc_name):
    stats = select(soup, "dd.stat-description")

    for stat in stats:

        stat_name_decs = select(stat, "li")
        if stat_name_decs:
            for stat_name in stat_name_decs:
                if select(stat_name, "span.title")[0].text == desc_name:
                    return select(stat_name, "span.stat-point")[0].text

def get_crit_rate(soup):
    return get_info_from_description(soup, "Critical Rate")

def get_cdmg(soup):
    return get_info_from_description(soup, "Increase Damage")

def get_accuracy(soup):
    return get_info_from_description(soup, "Hit Rate")

def get_guild(soup):
    guild = select(soup, "li.guild")

    if guild:
        return guild[0].text

def legendary_necklace_stage(soup):
    necklace = select(soup, "div.necklace")

    necklace = select(necklace[0], "img")[0]

    data_parts = necklace['item-data'].split(".")

    if data_parts[0] == "3300981":
        return data_parts[1]

    return False

extractors = collections.OrderedDict(
                [('AP', get_ap),
                 ('crit', get_crit_rate),
                 ('cdmg', get_cdmg),
                 ('piercing', get_piercing),
                 ('accuracy', get_accuracy),
                 ('guild', get_guild),
                 ('neck_stage', legendary_necklace_stage)])

async def get_character_info(name):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://eu-bns.ncsoft.com/ingame/bs/character/profile?c={}&s=213'.format(quote(name, safe='')), allow_redirects=False) as resp:

            if resp.status == 200:
                soup = Soup(await resp.read(), 'html.parser')

                results = collections.OrderedDict()
                for stat in extractors.items():
                    results[stat[0]] = stat[1](soup)

                return results
            else:
                return None