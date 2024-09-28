import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from gtts import gTTS

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync commands globally
        await self.tree.sync()

    async def on_ready(self):
        print('Bot is ready!')

# Function to generate TTS audio file
def gen_tts(text: str, lang: str = 'el'):
    tts = gTTS(text=text, lang=lang)
    tts.save('output.mp3')

def main() -> None:
    # Define the languages
    languages = {
        "bg": "Bulgarian", "de": "German", "el": "Greek", "en": "English", "es": "Spanish", "et": "Estonian",
        "fr": "French", "it": "Italian", "ja": "Japanese", "kn": "Kannada", "pt": "Portuguese (Brazil)",
        "ru": "Russian", "sq": "Albanian", "sv": "Swedish", "tr": "Turkish", "zh": "Chinese (Mandarin)"
    }

    # Fetch token from .env file
    token = ''
    with open('../.env', 'r') as fp:
        token = fp.readline().strip()

    # Define the bot instance
    bot = MyBot()

    # Generate the choices dynamically from the languages dictionary
    language_choices = [app_commands.Choice(name=name, value=code) for code, name in languages.items()]

    # Define the slash command for TTS
    @bot.tree.command(name="say", description="Say something in a specific language!")
    @app_commands.describe(
        text="The text you want to say",
        lang="Language to say it in"
    )
    @app_commands.choices(lang=language_choices)
    async def say(interaction: discord.Interaction, text: str, lang: str = 'el'):
        # Check if the user is in a voice channel
        if not interaction.user.voice:
            await interaction.response.send_message("You are not in a voice channel!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel

        # Generate TTS audio file
        gen_tts(text, lang)

        # Join the voice channel and play the mp3
        if voice_channel is not None:
            voice_client = await voice_channel.connect()

            if voice_client.is_connected():
                audio_source = discord.FFmpegPCMAudio('./output.mp3')

                # Play the generated mp3 file
                if not voice_client.is_playing():
                    voice_client.play(audio_source, after=lambda e: print(f"Finished playing: {e}"))

                    await interaction.response.send_message(
                        f"Playing your message in {languages.get(lang, 'Unknown Language')}!")

                # Disconnect after playing the audio
                while voice_client.is_playing():
                    await asyncio.sleep(1)

                await voice_client.disconnect()

        else:
            await interaction.response.send_message("Unable to join the voice channel.", ephemeral=True)

    # Run the bot
    bot.run(token)

if __name__ == '__main__':
    main()
