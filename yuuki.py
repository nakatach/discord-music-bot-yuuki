import nextcord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('bot_token')
    intents = nextcord.Intents.default()
    intents.message_content = True
    intents.presences = True
    intents.members = True
    client = nextcord.Client(intents=intents)

    voice_clients = {}
    yt_dlp_options = {"format" : "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dlp_options)

    ffmpeg_options = {'options' : '-vn'}

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')

    @client.event
    async def on_message(message):
        if message.content.startswith("/play"):
            if not message.author.voice:
                await message.channel.send("You need to be connected to a voice channel to play music.")
                return
            
            try:
                # Disconnect from voice channel if already connected
                if message.guild.id in voice_clients and voice_clients[message.guild.id].is_connected():
                    await voice_clients[message.guild.id].disconnect()
                
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
                print("Connected to voice channel")
            except Exception as e:
                print(f"Error connecting to the voice channel: {e}")
                await message.channel.send("Error connecting to the voice channel.")
                return

            try:
                url = message.content.split()[1]

                if not url:
                    await message.channel.send("Please provide a valid YouTube URL.")
                    return
                
                print(f"Fetching info for URL: {url}")

                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                song = data['url']
                print(f"Playing song: {song}")
                player = nextcord.FFmpegPCMAudio(song, **ffmpeg_options)

                voice_clients[message.guild.id].play(player)
                await message.channel.send(f"Now playing: {data['title']}")
            except Exception as e:
                print(f"Error playing the song: {e}")
                await message.channel.send("Error playing the song.")

        if message.content.startswith("/pause"):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)

        if message.content.startswith("/resume"):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)

        if message.content.startswith("/stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
            except Exception as e:
                print(e)

    client.run(TOKEN)
