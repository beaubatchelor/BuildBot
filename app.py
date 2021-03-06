#We should really add some comments to our code to give some flavor flave

import os, sys
sys.path.append(os.path.abspath('..'))
import requests
import discord
from discord import Client
from discord.ext.commands import Bot
# from config import discord_key, owners_ids ## Test
from functions.functions import (stat_table, mobi_champ_links, counter_message, stats_message,
                                 mobi_build_lookup, counter_champ_links, counter_champ_lookup,
                                 mobi_stats_lookup)

discord_key = os.environ.get('discord_key') ## Prod
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
counter_champ_links_dict = counter_champ_links()



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
        stat_list, stat_df = stat_table(champ_json, champ_id)
        win_stats_dict = mobi_stats_lookup(mobi_champ_links_dict[champ_name])
        ally = ', '.join(champ_detail_json['data'][champ_id]['allytips'])
        enemy = ', '.join(champ_detail_json['data'][champ_id]['enemytips'])
        
        embed=discord.Embed(title=f"{champ_name} Information", description=f"**Ally Tips**: {ally} \n **Enemy Tips**: {enemy}", color=0x0C223E)
        embed.add_field(name="Win Rate", value=f"{win_stats_dict['win']}", inline=True)
        embed.add_field(name="Ban Rate", value=f"{win_stats_dict['ban']}", inline=True)
        embed.add_field(name="Pick Rate", value=f"{win_stats_dict['pick']}", inline=True)
        await ctx.send(embed=embed)
        await ctx.send(f"```{stat_df[['Stat', '1', '2', '3', '4', '5', '6', '7', '8', '9']].to_string(index=False)}```")
        await ctx.send(f"```{stat_df[['Stat', '10', '11', '12', '13', '14', '15', '16', '17', '18']].to_string(index=False)}```")

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
        mobi_build_one, mobi_build_two, mobi_build_three = mobi_build_lookup(mobi_champ_links_dict[champ_name])
        embed=discord.Embed(title=f"Buildbot - {champ_name} Guide", url=f"{mobi_champ_links_dict[champ_name]}", color=0x0C223E)
        # embed.set_thumbnail(url=f"https://www.mobafire.com/images/champion/square/{clean_champ}.png")
        embed.add_field(name="**1.**", value=f"{mobi_build_one}", inline=False)
        embed.add_field(name="**2.**", value=f"{mobi_build_two}", inline=False)
        embed.add_field(name="**3.**", value=f"{mobi_build_three}", inline=False)
        await ctx.send(embed=embed)
    else:
        suggestion_list = list(filter(lambda x: x[0].lower() == clean_champ[0], champ_list))
        suggestion = ', '.join(suggestion_list)
        if suggestion_list == []:
            await ctx.send(f'We cannot find anything close to {champion}.')
        else:
            await ctx.send(f'We cannot find {champion}, Do you mean one of these? (character sensative) {suggestion}')


@build_bot.command()
async def counter(ctx, *, champion):
    clean_champ = str(champion).lower().replace(' ', '')
    if clean_champ in champ_list_lower:
        champ_name = champ_json['data'][champ_lookup[clean_champ]]['name']
        counter_champ_dict = counter_champ_lookup(counter_champ_links_dict[champ_name])
        best_list = counter_champ_dict['best']
        worst_list = counter_champ_dict['worst']
        embed=discord.Embed(title=f"Counter Picks for {champ_name}", url=f"{counter_champ_links_dict[champ_name]}", color=0x0C223E)
        embed.set_author(name="Build Bot", url="https://github.com/beaubatchelor/BuildBot/", icon_url="https://cdn.discordapp.com/attachments/774459422113267723/774725899270225950/Build_Bot_White.png")
        embed.add_field(name="#1 Best Picks Against", value=f"{best_list[0]['name']} {best_list[0]['percent']}", inline=True)
        embed.add_field(name="#2 Best Picks Against", value=f"{best_list[1]['name']} {best_list[1]['percent']}", inline=True)
        embed.add_field(name="#3 Best Picks Against", value=f"{best_list[2]['name']} {best_list[2]['percent']}", inline=True)
        embed.add_field(name="#1 Worst Picks Against", value=f"{worst_list[0]['name']} {worst_list[0]['percent']}", inline=True)
        embed.add_field(name="#2 Worst Picks Against", value=f"{worst_list[1]['name']} {worst_list[1]['percent']}", inline=True)
        embed.add_field(name="#3 Worst Picks Against", value=f"{worst_list[2]['name']} {worst_list[2]['percent']}", inline=True)
        await ctx.send(embed=embed)
    else:
        suggestion_list = list(filter(lambda x: x[0].lower() == clean_champ[0], champ_list))
        suggestion = ', '.join(suggestion_list)
        if suggestion_list == []:
            await ctx.send(f'We cannot find anything close to {champion}.')
        else:
            await ctx.send(f'We cannot find {champion}, Do you mean one of these? (character sensative) {suggestion}')

# @build_bot.command()
# async def displayembed(ctx):
#     embed = discord.Embed(title = "Buildbot - {champion} Guide", description = "test", color = 0x0C223E)
#         # url = "https://www.google.com", #link to guide

#     embed.set_image(url='https://media.discordapp.net/attachments/774455803137753128/774544353477656616/4lf322.png')
#     embed.set_thumbnail(url='https://media.discordapp.net/attachments/774455803137753128/774544353477656616/4lf322.png')
#     embed.set_author(name='blue'),
#     embed.add_field(name='Primary Runes', value = 'field value, inline=False'),
#     embed.add_field(name='Secondary Runes', value = 'field value, inline=True'),
#     embed.add_field(name='Bonus Runes', value = 'field value, inline=True'),

#     embed.set_author(name='John'),
#     embed.set_footer(text='Link 1.\n Link 2.') # , icon_url = bot.user.avatar_url

#     await ctx.send(embed = embed)

@build_bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(title = "Buildbot - Guide", description = "BuildBot is a bot made with the intent to help League of Legends players enhance their ranked experience", color = 0x0C223E)
    # embed.set_image(url='data\Build_Bot_White.png') ## waiting for git post
    embed.add_field(name = 'Build Links', value = '\n "!bb build [champ]" Provides the best builds for that champion as per our algorithm.', inline=False),
    embed.add_field(name = 'Counters', value = '\n "!bb counter [champ]" Provides best and worst picks against given champion.', inline=False),
    embed.add_field(name = 'Statistics', value = '\n "!bb stats [champ]" Provides statistics about a given character for anyone who might require them.', inline=False),
    embed.set_footer(text='https://github.com/beaubatchelor/BuildBot')

    await ctx.send(embed = embed)

build_bot.run(discord_key)
