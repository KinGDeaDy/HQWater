from HQApi import HQApi
from threading import Lock, Thread
import random
import traceback
import sqlite3
from sqlite3worker import Sqlite3Worker
import requests
import time
import concurrent.futures
import numpy

lock=Lock()
worker = Sqlite3Worker("answers.db")

db2 = sqlite3.connect("../Live Game/hqwater.db")
cursor2 = db2.cursor()
cursor2.execute("SELECT * FROM accounts")
res = cursor2.fetchall()
tokens = []
for r in res:
    tokens.append({"token": r[0], "proxy": r[1].replace("https", "http")})


def win_game(sliced_tokens):
    for i in sliced_tokens:
        t=tokens[i]
        print("Аккаунт №"+str(i))
        api = HQApi(t["token"], proxy=t["proxy"])
        while int(api.get_users_me()["coins"])//100<4 and api.get_users_me()["lives"]<1:
            print("У меня "+str(api.get_users_me()["coins"])+"монет")
            try:
                offair_id = api.start_offair()['gameUuid']
            except:
                try:
                    offair_id = api.get_schedule()['offairTrivia']['games'][0]['gameUuid']
                except:
                    break
            while True:
                offair = api.offair_trivia(offair_id)
                #print("Question {0}/{1}".format(offair['question']['questionNumber'], offair['questionCount']))
                #print(offair['question']['question'])
                res = worker.execute("SELECT EXISTS (SELECT answer FROM answers WHERE text = ?)", (offair['question']['question'],))
                if res[0][0]:
                    res = worker.execute("SELECT answer FROM answers WHERE text = ?", (offair['question']['question'],))
                    correct = res[0][0]
                    select = None
                    for answer in offair['question']['answers']:
                        if correct == answer["text"]:
                            select = offair['question']['answers'].index(answer)
                    if select!=None:
                        answer = api.send_offair_answer(offair_id, offair['question']['answers'][select]['offairAnswerId'])
                    else:
                        select = random.randint(1, 3)
                        answer = api.send_offair_answer(offair_id, offair['question']['answers'][select - 1]['offairAnswerId'])
                    #print('You got it right: ' + str(answer['youGotItRight']))
                    #for ans in answer["answerCounts"]:
                        #if ans["correct"]:
                            #print("Correct answer", ans["answer"])
                else:
                    select = random.randint(1, 3)
                    #for answer in offair['question']['answers']['offairAnswerId']:
                    answer = api.send_offair_answer(offair_id, offair['question']['answers'][select - 1]['offairAnswerId'])
                    #print('You got it right: ' + str(answer['youGotItRight']))
                    for ans in answer["answerCounts"]:
                        if ans["correct"]:
                            #print("Correct answer", ans["answer"])
                            try:
                                worker.execute("INSERT into answers values (?, ?)",
                                                   (offair['question']['question'], ans["answer"]))
                            except:
                                print("Answer was already in db")
                if answer['gameSummary']:
                    print('Game ended')
                    print('Earned:')
                    print('Coins: ' + str(answer['gameSummary']['coinsEarned']))
                    print('Points: ' + str(answer['gameSummary']['pointsEarned']))
                    break
l = numpy.array_split(numpy.array(range(len(tokens))),10)
for i in l:
    Thread(target=win_game,args=(i,)).start()
