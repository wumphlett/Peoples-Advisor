import re
from datetime import datetime

import requests

"""
The functions here make use of webscraping oanda and do not use the official oanda api
Use at your own risk
"""


def get_historical_spreads(instrument: str, since: datetime):
    """
    Get a list of historical spreads for a given forex pair

    Args:
        instrument (str): The instrument to filter the requested orders by
            see InstrumentName in oanda_guide.txt
        since (datetime): A datetime object to retrieve all spread data after
    """
    time_diff = str(int(datetime.now().timestamp() - since.timestamp()))
    headers = {"Content-Type": "application/json"}
    r = requests.get(
        f"https://www.oanda.com/labsds/calendar_and_spreads?period={time_diff}&instrument={instrument}",
        headers=headers,
    )
    return r.json()["spreads"]["avg"]


def get_all_current_prices():
    """
    Get a dictionary of all current forex pairs and their prices offered by oanda.
    NOTE: This is not an official endpoint and has been intentionally obfuscated by oanda. Use at your own risk.

    How this is accomplished:
    The first call (assigned to data) retrieves the encrypted hex string that contains all of the current oanda prices.
    Next, the rc4 key is obtained in a way that, should oanda change random ids, the key should still be scraped.
    Next, the hex string is decoded in the same manner oanda does this (converted from js to python).
    Lastly, the decoded hex string is decrypted with the scraped key using the rc4 algorithm.
    """
    data = requests.get(f"https://www.oanda.com/lfr/rates_all").text
    spreads = requests.get("https://www1.oanda.com/forex-trading/markets/recent").text
    rc4_js = requests.get("https://www.oanda.com" + re.search(r"/wandacache/rc4-[0-9a-f]+\.js", spreads).group()).text
    rc4_key = re.search('var key="[0-9a-f]+"', rc4_js).group()[9:-1]
    return _to_price_dict(_rc4decrypt(rc4_key, _hex_decode(data)))


def _hex_decode(hex_str):
    if len(hex_str) % 2:
        hex_str = "0" + hex_str
    decode = [chr(int(hex_str[(i * 2) : (i * 2) + 2], 16)) for i in range(len(hex_str) // 2)]
    return "".join(decode)


def _rc4decrypt(key, cypher):
    # Key-scheduling algorithm (KSA)
    key_schedule = [i for i in range(256)]
    j = 0
    for i in range(256):
        j = (j + key_schedule[i] + ord(key[i % len(key)])) % 256
        key_schedule[i], key_schedule[j] = key_schedule[j], key_schedule[i]
    # Pseudo-random generation algorithm (PRGA)
    c = []
    i = 0
    j = 0
    for k in range(len(cypher)):
        i = (i + 1) % 256
        j = (j + key_schedule[i]) % 256
        key_schedule[i], key_schedule[j] = key_schedule[j], key_schedule[i]
        c.append(chr(ord(cypher[k]) ^ key_schedule[(key_schedule[i] + key_schedule[j]) % 256]))
    return "".join(c)


def _to_price_dict(price_text):
    prices = {}
    for line in price_text.split("\n"):
        line = line.split("=")
        prices.update({line[0]: {"bid": line[1], "ask": line[2], "spread": line[4]}})
    return prices
