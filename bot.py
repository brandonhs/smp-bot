import os
import sys

from urllib.parse import urlparse

import discord
from discord.ext import commands

from dotenv import load_dotenv
from periodic import Periodic
from mcpacket import protocol

from pyngrok import ngrok

import argparse

parser = argparse.ArgumentParser(description='Run the CAMS SMP discord bot', epilog='If no hostname is provided, an ngrok server will be started from localhost.')
parser.add_argument('--hostname', required = False, type=str, help='The hostname of the server')
parser.add_argument('--port', required = False, type=int, help='The port of the server')
parser.add_argument('--token', required = False, type=str, help='The token of the discord bot')

args = parser.parse_args()

hostname = args.hostname
port = args.port
token = args.token

if not token:
    load_dotenv()
    token = os.environ.get('TOKEN')

if not args.hostname:
    tunnel = ngrok.connect(25565, 'tcp')
    ngrok_url = tunnel.public_url
    ngrok_parsed = urlparse(ngrok_url)
    hostname = ngrok_parsed.hostname
    port = ngrok_parsed.port
if not port:
    port = 25565

print(hostname, port)

protoc = protocol.Protocol(host=hostname, port=port)
protoc.connect()

bot = commands.Bot('$')

async def update_status():
    protoc.connect()
    await bot.change_presence(activity=discord.Game(f'{hostname}:{port} with {protoc.player_count}/{protoc.player_max} online players'))

@bot.command()
async def smpinfo(ctx: commands.Context):
    protoc.connect()
    msg = ''
    msg += f'{protoc.description.text}\n'
    msg += f'IP: `{hostname}:{port}`\n\n'
    msg += f'Online Players: `{protoc.player_count}/{protoc.player_max}`\n'
    msg += '\n'
    for player in protoc.player_list:
        msg += f'**{player.name}** - `{player.id}`\n'
    await ctx.send(msg)

async def main():
    p = Periodic(3, update_status)
    await p.start()


loop = bot.loop
loop.create_task(main())
bot.run(token)
