from HQApi import HQApi
from threading import Thread
import random
from sqlite3worker import Sqlite3Worker
import traceback

sql_worker = Sqlite3Worker("answers.db")
with open("tokens.txt") as f:
    tokens = f.read().split("\n")
import sqlite3

db = sqlite3.connect("answers.db")
cursor = db.cursor()


def play_game():
    while True:
        try:
            token = random.choice(tokens)
            # tokens.remove(token)
            # print(token)
            api = HQApi(logintoken=token)

            try:
                offair_id = api.start_offair()['gameUuid']
            except:
                offair_id = api.get_schedule()['offairTrivia']['games'][0]['gameUuid']
            while True:
                offair = api.offair_trivia(offair_id)
                print("Question {0}/{1}".format(offair['question']['questionNumber'], offair['questionCount']))
                print(offair['question']['question'])
                for answer in offair['question']['answers']:
                    print(answer["text"])
                select = random.randint(1, 3)
                answer = api.send_offair_answer(offair_id, offair['question']['answers'][select - 1]['offairAnswerId'])
                print('You got it right: ' + str(answer['youGotItRight']))
                for ans in answer["answerCounts"]:
                    if ans["correct"]:
                        print("Correct answer", ans["answer"])
                        try:
                            sql_worker.execute("INSERT into answers values (?, ?)",
                                               (offair['question']['question'], ans["answer"]))
                        except:
                            print("Answer was already in db")

                if answer['gameSummary']:
                    print('Game ended')
                    print('Earned:')
                    print('Coins: ' + str(answer['gameSummary']['coinsEarned']))
                    print('Points: ' + str(answer['gameSummary']['pointsEarned']))
                    break
        except:
            traceback.print_exc()


# play_game()
def win_game():
    # token = random.choice(tokens)
    token = random.choice(tokens)
    api = HQApi(logintoken=token)
    print(token)
    # tokens.remove(token)
    # print(token)
    # print(api.get_users_me()["coins"])
    
    try:
        offair_id = api.start_offair()['gameUuid']
    except:
        offair_id = api.get_schedule()['offairTrivia']['games'][0]['gameUuid']
    while True:
        offair = api.offair_trivia(offair_id)
        print("Question {0}/{1}".format(offair['question']['questionNumber'], offair['questionCount']))
        print(offair['question']['question'])
        res = sql_worker.execute("SELECT EXISTS (SELECT answer FROM answers WHERE text = ?)", (offair['question']['question'],))
        if res[0][0]:
            res = sql_worker.execute("SELECT answer FROM answers WHERE text = ?", (offair['question']['question'],))
            correct = res[0][0]
            select = None
            for answer in offair['question']['answers']:
                if correct == answer["text"]:
                    select = offair['question']['answers'].index(answer)
            answer = api.send_offair_answer(offair_id, offair['question']['answers'][select]['offairAnswerId'])
        else:
            select = random.randint(1, 3)
            answer = api.send_offair_answer(offair_id, offair['question']['answers'][select - 1]['offairAnswerId'])
            print('You got it right: ' + str(answer['youGotItRight']))
            for ans in answer["answerCounts"]:
                if ans["correct"]:
                    print("Correct answer", ans["answer"])
                    try:
                        sql_worker.execute("INSERT into answers values (?, ?)",
                                           (offair['question']['question'], ans["answer"]))
                    except:
                        print("Answer was already in db")
        if answer['gameSummary']:
            print('Game ended')
            print(api.get_users_me())
            print('Earned:')
            print('Coins: ' + str(answer['gameSummary']['coinsEarned']))
            print('Points: ' + str(answer['gameSummary']['pointsEarned']))
            break

# token = random.choice(tokens)
#
# while True:
#     win_game(token)
for i in range(400):
    t = Thread(target=win_game)
    t.start()