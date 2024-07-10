import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from random import shuffle

# Указываем намерения
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Указываем префикс команд и создаем объект бота
bot = commands.Bot(command_prefix="!", intents=intents)

# Очередь воспроизведения
queue = []

# Сообщение при запуске бота
@bot.event
async def on_ready():
    await bot.tree.sync()  # Синхронизация слэш-команд с Discord
    print(f'Bot {bot.user.name} has connected to Discord!')

# Команда для присоединения к голосовому каналу
@bot.tree.command(name="join", description="Команда для присоединения к голосовому каналу")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"Подключен к {channel}", ephemeral=True)
    else:
        await interaction.response.send_message("Вы должны быть в голосовом канале, чтобы использовать эту команду.", ephemeral=True)

# Команда для выхода из голосового канала
@bot.tree.command(name="leave", description="Команда для выхода из голосового канала")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Отключен от голосового канала", ephemeral=True)
    else:
        await interaction.response.send_message("Бот не в голосовом канале.", ephemeral=True)

# Команда для остановки текущей музыки
@bot.tree.command(name="stop", description="Команда для остановки текущей музыки")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Воспроизведение остановлено", ephemeral=True)
    else:
        await interaction.response.send_message("Сейчас ничего не проигрывается.", ephemeral=True)

# Функция для воспроизведения следующего трека из очереди
async def play_next(ctx):
    if queue:
        url = queue.pop(0)
        await play_from_queue(ctx, url)

# Функция для воспроизведения трека из очереди
async def play_from_queue(ctx, url):
    try:
        server = ctx.guild
        voice_channel = server.voice_client

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'auto',
            'quiet': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info['url']

            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }

            voice_channel.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

        await ctx.send(f'Проигрывается: {info["title"]}')
    except Exception as e:
        await ctx.send(f'Произошла ошибка: {str(e)}')

# Команда для добавления трека в очередь
@bot.tree.command(name="play", description="Команда для добавления трека в очередь")
async def play(interaction: discord.Interaction, url: str):
    queue.append(url)
    await interaction.response.send_message(f'Добавлено в очередь: {url}', ephemeral=True)
    if not interaction.guild.voice_client.is_playing():
        await play_next(interaction)

# Команда для просмотра очереди
@bot.tree.command(name="queue", description="Команда для просмотра очереди")
async def view_queue(interaction: discord.Interaction):
    if queue:
        await interaction.response.send_message(f'Очередь:\n' + '\n'.join(queue), ephemeral=True)
    else:
        await interaction.response.send_message('Очередь пуста.', ephemeral=True)

# Команда для удаления трека из очереди
@bot.tree.command(name="remove", description="Команда для удаления трека из очереди")
async def remove(interaction: discord.Interaction, index: int):
    try:
        removed = queue.pop(index - 1)
        await interaction.response.send_message(f'Удалено из очереди: {removed}', ephemeral=True)
    except IndexError:
        await interaction.response.send_message('Неверный индекс.', ephemeral=True)

# Команда для перемешивания очереди
@bot.tree.command(name="shuffle", description="Команда для перемешивания очереди")
async def shuffle_queue(interaction: discord.Interaction):
    shuffle(queue)
    await interaction.response.send_message('Очередь перемешана.', ephemeral=True)

# Запуск бота
bot.run('MTA0MjM4MzkyNzEwNjYwNTA3Ng.GNGL1F.lMt_oAsw9oT6rJE5mdm3GzAHMF_TxG_sSXsHlY')
