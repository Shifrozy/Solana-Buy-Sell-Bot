import os
import json
import time
import requests
from decimal import Decimal
from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client

import base58


# Load env
load_dotenv()
RPC_URL = os.getenv("RPC_URL", "https://api.devnet.solana.com")
KEYPAIR_PATH = os.getenv("KEYPAIR_PATH")
KEYPAIR_B58 = os.getenv("KEYPAIR_B58")

# Load wallet
def load_keypair():
    if KEYPAIR_PATH and os.path.exists(KEYPAIR_PATH):
        with open(KEYPAIR_PATH, "r") as f:
            arr = json.load(f)
        return Keypair.from_secret_key(bytes(arr))
    if KEYPAIR_B58:
        raw = base58.b58decode(KEYPAIR_B58)
        return Keypair.from_secret_key(raw)
    raise Exception("No keypair set in .env")

wallet = load_keypair()
print("Bot Wallet:", wallet.public_key)

# Solana client
client = Client(RPC_URL)

# Example token (replace with your new token’s mint address on Devnet)
TOKEN_MINT = "So11111111111111111111111111111111111111112"  # SOL-wrapped placeholder
PAIR = f"SOL-{TOKEN_MINT}"

# Strategy params
ENTRY_PRICE = None
POSITION = False
BUY_AMOUNT_SOL = 0.1

TAKE_PROFIT_BUY = Decimal("1.01")  # +1% trigger
TAKE_PROFIT_SELL = Decimal("1.02") # +2% sell
STOP_LOSS = Decimal("0.99")        # -1% stop loss

# Jupiter price API
def get_price():
    url = f"https://price.jup.ag/v4/price?ids={PAIR}&vsToken=USDC"
    resp = requests.get(url).json()
    try:
        return Decimal(resp["data"][PAIR]["price"])
    except Exception:
        return None

# Simulated buy/sell (replace with Jupiter swap TX later)
def buy(price):
    global ENTRY_PRICE, POSITION
    ENTRY_PRICE = price
    POSITION = True
    print(f"[BUY] Bought {BUY_AMOUNT_SOL} SOL worth of token at {price} USDC")

def sell(price):
    global ENTRY_PRICE, POSITION
    print(f"[SELL] Sold at {price} USDC")
    ENTRY_PRICE = None
    POSITION = False

# Bot loop
while True:
    price = get_price()
    if not price:
        print("Price fetch failed...")
        time.sleep(5)
        continue

    print("Current price:", price)

    if not POSITION:
        # First buy
        buy(price)
    else:
        change = price / ENTRY_PRICE
        if change >= TAKE_PROFIT_SELL:
            sell(price)
        elif change >= TAKE_PROFIT_BUY:
            print(f"[RE-BUY TRIGGER] Price +1% at {price}, would buy more here...")
        elif change <= STOP_LOSS:
            sell(price)

    time.sleep(10)
