import os, sys
sys.path.append(os.path.abspath('..'))
import requests
import discord
from discord import Client
from discord.ext.commands import Bot
# from config import discord_key, owners_ids ## Test
from functions.functions import stat_table, mobi_champ_links, mobi_build_lookup

discord_key = os.environ.get('discord_key') ## Prod
discord_key = 'Nzc0MTUxOTgwMTU5MjA1Mzc4.X6TnNw.34L3T9QlIpyeMieofmV8LwZ2tek'
command_prefix = '!bb '

build_bot = Bot(command_prefix=command_prefix) ## Prod
# build_bot = Bot(command_prefix=command_prefix,
#                  owner_ids=list(owners_ids.values())) ## Test


## Connection to the Champion API
version_list = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()
latest_version = version_list[0]
champ_json = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json').json()
champ_list = list(champ_json['data'].keys())
champ_list_lower = list(map(lambda x: x.lower().replace(' ', ''), champ_list))
champ_lookup = {champ_list_lower[i]: champ_list[i] for i in range(len(champ_list_lower))}
mobi_champ_links_dict = mobi_champ_links()



@build_bot.event
async def on_ready():
    print(f'Bot connected as {build_bot.user}')

@build_bot.command()
async def stats(ctx, *, champion):
    clean_champ = str(champion).lower().replace(' ', '')
    if clean_champ in champ_list_lower:
        champ_name = champ_json['data'][champ_lookup[clean_champ]]['name']
        champ_id = champ_json['data'][champ_lookup[clean_champ]]['id']
        champ_detail_json = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion/{champ_id}.json').json()
        ally = ', '.join(champ_detail_json['data'][champ_id]['allytips'])
        enemy = ', '.join(champ_detail_json['data'][champ_id]['enemytips'])

        stat_list, stat_df = stat_table(champ_json, champ_id)

        await ctx.send(f"You have chosen {champ_name}")
        await ctx.send(f"```{stat_df[['Stat', '1', '2', '3', '4', '5', '6', '7', '8', '9']].to_string(index=False)}```")
        await ctx.send(f"```{stat_df[['Stat', '10', '11', '12', '13', '14', '15', '16', '17', '18']].to_string(index=False)}```")
        await ctx.send(f"Ally Tips: {ally}")
        await ctx.send(f"Enemy Tips: {enemy}")

    else:
        suggestion_list = list(filter(lambda x: x[0].lower() == clean_champ[0], champ_list))
        suggestion = ', '.join(suggestion_list)
        if suggestion_list == []:
            await ctx.send(f'We cannot find anything close to {champion}.')
        else:
            await ctx.send(f'We cannot find {champion}, Do you mean one of these? (character sensative) {suggestion}')

@build_bot.command()
async def build(ctx, *, champion):
    clean_champ = str(champion).lower().replace(' ', '')
    if clean_champ in champ_list_lower:
        champ_name = champ_json['data'][champ_lookup[clean_champ]]['name']
        mobi_build = mobi_build_lookup(mobi_champ_links_dict[champ_name])
        await ctx.send(f"Mobifire Build: <{mobi_build}>")
    else:
        suggestion_list = list(filter(lambda x: x[0].lower() == clean_champ[0], champ_list))
        suggestion = ', '.join(suggestion_list)
        if suggestion_list == []:
            await ctx.send(f'We cannot find anything close to {champion}.')
        else:
            await ctx.send(f'We cannot find {champion}, Do you mean one of these? (character sensative) {suggestion}')

@build_bot.command()
async def displayembed(ctx):
    embed = discord.Embed(title = "Buildbot - {champion} Guide", description = "test", color = 0x0C223E)
        # url = "https://www.google.com", #link to guide

    embed.set_image(url='https://media.discordapp.net/attachments/774455803137753128/774544353477656616/4lf322.png')
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/774455803137753128/774544353477656616/4lf322.png')
    embed.set_author(name='blue'),
    embed.add_field(name='Primary Runes', value = 'field value, inline=False'),
    embed.add_field(name='Secondary Runes', value = 'field value, inline=True'),
    embed.add_field(name='Bonus Runes', value = 'field value, inline=True'),

    embed.set_author(name='John'),
    embed.set_footer(text='Link 1.\n Link 2.') # , icon_url = bot.user.avatar_url

    await ctx.send(embed = embed)

build_bot.run(discord_key)