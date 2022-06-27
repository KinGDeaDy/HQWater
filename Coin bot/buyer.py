from HQApi import HQApi
from threading import Thread
import random
import traceback
import sqlite3
from sqlite3worker import Sqlite3Worker
import requests
import time
worker = Sqlite3Worker("answers.db")

db2 = sqlite3.connect("../Live Game/hqwater.db")
cursor2 = db2.cursor()
cursor2.execute("SELECT * FROM accounts")
res = cursor2.fetchall()
tokens = []
for r in res:
    tokens.append({"token": r[0], "proxy": r[1].replace("https", "http")})


ERROR_COUNT = 0
PRX = []

def buy_coins(t):
  r = requests.post("https://api-quiz.hype.space/store/com.intermedia.hq.item.extralife.1x/purchase",
                    headers={"Authorization": "Bearer " + t["token"]},
                    proxies={"http": t["proxy"], "https": t["proxy"]},
                    json={
                        "metadata": {
                            "buyBackIn": False
                        }
                    })
  print(r.json())


threads = []
# for t in tokens:
#     threads.append(Thread(target=win_game, args=(t,)).start())
for t in tokens:
    threads.append(Thread(target=buy_coins, args=(t,)).start())
    time.sleep(1)
