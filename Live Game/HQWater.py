# todo accounts tab, surveys, google search, answer bot
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from functools import partial
from HQApi import HQApi, HQWebSocket
import json
from threading import Thread
import time
from PyQt5.QtWidgets import QAbstractItemView, QInputDialog, QLabel
from lomond.persist import persist
import sqlite3
import traceback
from qt_material import apply_stylesheet

total=0
def alert(title, subtitle="", text="", additional="", icon=1, callback=None, font=None):
    msg = QtWidgets.QMessageBox()
    msg.setText(subtitle)
    if text:
        msg.setInformativeText(text)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    if additional:
        msg.setDetailedText(additional)
    if callable(callback):
        msg.buttonClicked.connect(callback)
        msg.closeEvent = callback
    if font:
        msg.setFont(font)
    msg.exec()


class Checker(QtCore.QThread):
    signal = QtCore.pyqtSignal(dict)
    def __init__(self, token):
        super(Checker, self).__init__()
        self.t = token
    def run(self):
        global proxy
        global total
        try:
            if self.t["proxy"] == None or self.t["proxy"] == "":
                hq = HQApi(self.t["token"])
            else:
                hq = HQApi(self.t["token"], proxy=self.t['proxy'])
            me = hq.get_users_me()
            pay = hq.get_payouts_me()
            #print(pay["recentWins"])
            if pay["balance"]["eligibleForPayout"]:
                ban = False
            elif pay["balance"]["payoutEligibility"] == "disallowed_all_frozen":
                ban = "Frozen"
            elif pay["balance"]["payoutEligibility"] == "disallowed_banned":
                ban = "Permanent ban"
            elif pay["balance"]["payoutEligibility"] == "disallowed_not_enough":
                ban = "Not enough"
            else:
                ban = pay["balance"]["payoutEligibility"]
            total+=float(pay["balance"]["available"].replace("$",""))
            if pay["balance"]["available"][1:]=="0":
                print()
            print(pay["balance"]["available"][1:])
            self.signal.emit(
                {"nickname": me["username"], "lifes": me["lives"], "money_all": pay["balance"]["available"],
                 "money_un": pay["balance"]["unpaid"], "token": self.t["token"], "ban": ban})
            #print(total)
        except Exception as e:
            print(e)


try:
    db = sqlite3.connect("hqwater.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM accounts")
    res = cursor.fetchall()
    tokens = []
    for r in res:
        tokens.append({"token": r[0], "proxy": r[1].replace("https", "http")})
    grand_token = tokens[0]
    print(grand_token)
    all_tokens = json.loads(json.dumps(tokens))
    tokens.remove(tokens[0])


    class Ui_HQWater(object):
        def setupUi(self, HQWater):
            HQWater.setObjectName("HQWater")
            HQWater.resize(820, 601)
            app_icon = QtGui.QIcon()
            app_icon.addFile('icon/water.png', QtCore.QSize(32,32))
            app.setWindowIcon(app_icon)
            self.centralwidget = QtWidgets.QWidget(HQWater)
            self.centralwidget.setObjectName("centralwidget")
            self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
            self.verticalLayout.setObjectName("verticalLayout")
            self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
            font = QtGui.QFont()
            font.setPointSize(8)
            self.tabWidget.setFont(font)
            self.tabWidget.setObjectName("tabWidget")
            self.account_tab = QtWidgets.QWidget()
            self.account_tab.setObjectName("account_tab")
            self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.account_tab)
            self.verticalLayout_4.setObjectName("verticalLayout_4")
            self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
            self.tableWidget.setObjectName("table")
            self.verticalLayout_4.addWidget(self.tableWidget)
            self.tabWidget.addTab(self.account_tab, "")
            self.game_tab = QtWidgets.QWidget()
            self.game_tab.setObjectName("game_tab")
            self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.game_tab)
            self.verticalLayout_2.setObjectName("verticalLayout_2")
            self.questionBox = QtWidgets.QGroupBox(self.game_tab)
            font = QtGui.QFont()
            font.setPointSize(8)
            self.questionBox.setFont(font)
            self.questionBox.setTitle("")
            self.questionBox.setObjectName("questionBox")
            self.gridLayout_2 = QtWidgets.QGridLayout(self.questionBox)
            self.gridLayout_2.setVerticalSpacing(2)
            self.gridLayout_2.setObjectName("gridLayout_2")
            self.connectButton = QtWidgets.QPushButton(self.questionBox)
            self.connectButton.setObjectName("connectButton")
            self.gridLayout_2.addWidget(self.connectButton, 0, 1, 1, 1)
            font = QtGui.QFont()
            font.setPointSize(8)
            self.aliveAccountsLabel = QtWidgets.QLabel(self.questionBox)
            self.aliveAccountsLabel.setObjectName("aliveAccountsLabel")
            self.gridLayout_2.addWidget(self.aliveAccountsLabel, 0, 5, 1, 1)
            self.nextShowLabel = QtWidgets.QLabel(self.questionBox)
            self.nextShowLabel.setObjectName("nextShowLabel")
            self.streakLabel = QLabel()
            self.gridLayout_2.addWidget(self.streakLabel, 0, 3, 1, 1)
            self.correctLabel = QLabel()
            self.gridLayout_2.addWidget(self.correctLabel, 0, 2, 1, 1)
            self.gridLayout_2.addWidget(self.nextShowLabel, 0, 4, 1, 1)
            self.verticalLayout_3 = QtWidgets.QVBoxLayout()
            self.verticalLayout_3.setObjectName("verticalLayout_3")
            self.questionLabel = QtWidgets.QLabel(self.questionBox)
            self.questionNumberLabel = QLabel()
            self.gridLayout_2.addWidget(self.questionNumberLabel,1,6,1,1)
            self.questionNumberLabel.setAlignment(QtCore.Qt.AlignRight)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.questionLabel.sizePolicy().hasHeightForWidth())
            self.questionLabel.setSizePolicy(sizePolicy)
            self.questionLabel.setObjectName("questionLabel")
            self.verticalLayout_3.addWidget(self.questionLabel)
            self.variant1 = QtWidgets.QLabel(self.questionBox)
            self.variant1.setObjectName("variant1")
            self.verticalLayout_3.addWidget(self.variant1)
            self.variant2 = QtWidgets.QLabel(self.questionBox)
            self.variant2.setObjectName("variant2")
            self.verticalLayout_3.addWidget(self.variant2)
            self.variant3 = QtWidgets.QLabel(self.questionBox)
            self.variant3.setObjectName("variant3")
            self.verticalLayout_3.addWidget(self.variant3)
            self.gridLayout_2.addLayout(self.verticalLayout_3, 1, 1, 1, 5)
            self.verticalLayout_2.addWidget(self.questionBox)
            self.answerSelectionBox = QtWidgets.QGroupBox(self.game_tab)
            self.answerSelectionBox.setTitle("")
            self.answerSelectionBox.setObjectName("answerSelectionBox")
            self.gridLayout = QtWidgets.QGridLayout(self.answerSelectionBox)
            self.gridLayout.setObjectName("gridLayout")
            self.verticalLayout_2.addWidget(self.answerSelectionBox)
            self.tabWidget.addTab(self.game_tab, "")
            self.verticalLayout.addWidget(self.tabWidget)
            HQWater.setCentralWidget(self.centralwidget)
            self.menubar = QtWidgets.QMenuBar(HQWater)
            self.menubar.setGeometry(QtCore.QRect(0, 0, 820, 26))
            self.menubar.setObjectName("menubar")
            HQWater.setMenuBar(self.menubar)
            self.statusbar = QtWidgets.QStatusBar(HQWater)
            self.statusbar.setObjectName("statusbar")
            HQWater.setStatusBar(self.statusbar)

            self.retranslateUi(HQWater)
            self.tabWidget.setCurrentIndex(1)
            QtCore.QMetaObject.connectSlotsByName(HQWater)

        def retranslateUi(self, HQWater):
            _translate = QtCore.QCoreApplication.translate
            HQWater.setWindowTitle(_translate("HQWater", "HQWater"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.account_tab), _translate("HQWater", "Accounts"))
            self.connectButton.setText(_translate("HQWater", "Connect"))
            self.aliveAccountsLabel.setText(_translate("HQWater", "Alive accounts"))
            self.nextShowLabel.setText(_translate("HQWater", "Next show"))
            self.questionLabel.setText(_translate("HQWater", "Question"))
            self.variant1.setText(_translate("HQWater", "Answer 1"))
            self.variant2.setText(_translate("HQWater", "Answer 2"))
            self.variant3.setText(_translate("HQWater", "Answer 3"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.game_tab), _translate("HQWater", "Game"))

        def show_ans_buttons(self):
            self.answerSelectionBox.hide()
            self.answerSelectionBox = QtWidgets.QGroupBox(self.game_tab)
            self.answerSelectionBox.setTitle("")
            self.answerSelectionBox.setObjectName("answerSelectionBox")
            self.gridLayout = QtWidgets.QGridLayout(self.answerSelectionBox)
            self.gridLayout.setObjectName("gridLayout")
            self.extraLifeBtn = QtWidgets.QPushButton(self.answerSelectionBox)
            self.extraLifeBtn.setObjectName("extraLifeBtn")
            self.gridLayout.addWidget(self.extraLifeBtn, 2, 2, 1, 1)
            self.ans123 = QtWidgets.QPushButton(self.answerSelectionBox)
            self.ans123.setObjectName("ans123")
            self.gridLayout.addWidget(self.ans123, 2, 1, 1, 1)
            self.ans13 = QtWidgets.QPushButton(self.answerSelectionBox)
            self.ans13.setObjectName("ans13")
            self.gridLayout.addWidget(self.ans13, 1, 2, 1, 1)
            self.ans23 = QtWidgets.QPushButton(self.answerSelectionBox)
            self.ans23.setObjectName("ans23")
            self.gridLayout.addWidget(self.ans23, 1, 1, 1, 1)
            self.ans2 = QtWidgets.QPushButton(self.answerSelectionBox)
            self.ans2.setObjectName("ans2")
            self.gridLayout.addWidget(self.ans2, 0, 1, 1, 1)
            self.ans1 = QtWidgets.QPushButton(self.answerSelectionBox)
            self.ans1.setObjectName("ans1")
            self.gridLayout.addWidget(self.ans1, 0, 0, 1, 1)
            self.ans12 = QtWidgets.QPushButton(self.answerSelectionBox)
            self.ans12.setObjectName("ans12")
            self.gridLayout.addWidget(self.ans12, 1, 0, 1, 1)
            self.ans3 = QtWidgets.QPushButton(self.answerSelectionBox)
            self.ans3.setObjectName("ans3")
            self.gridLayout.addWidget(self.ans3, 0, 2, 1, 1)
            self.verticalLayout_2.addWidget(self.answerSelectionBox)
            self.extraLifeBtn.setText('Extra Life')
            self.ans1.setText('1')
            self.ans2.setText('2')
            self.ans3.setText('3')
            self.ans12.setText('12')
            self.ans23.setText('23')
            self.ans13.setText('13')
            self.ans123.setText('123')

        def show_checkpoint_buttons(self):
            self.verticalLayout_5 = QtWidgets.QVBoxLayout()
            self.verticalLayout_5.setObjectName("verticalLayout_5")
            self.numToWinInput = QtWidgets.QLineEdit(self.answerSelectionBox)
            self.numToWinInput.setText("")
            self.numToWinInput.setObjectName("numToWinInput")
            self.verticalLayout_5.addWidget(self.numToWinInput)
            self.confirmToWinInput = QtWidgets.QPushButton(self.answerSelectionBox)
            self.confirmToWinInput.setObjectName("confirmToWinInput")
            self.verticalLayout_5.addWidget(self.confirmToWinInput)
            self.gridLayout.addLayout(self.verticalLayout_5, 2, 1, 1, 3)
            self.winOnHalfBtn = QtWidgets.QPushButton(self.answerSelectionBox)
            self.winOnHalfBtn.setObjectName("winOnHalfBtn")
            self.gridLayout.addWidget(self.winOnHalfBtn, 1, 2, 1, 1)
            self.winOnThirdBtn = QtWidgets.QPushButton(self.answerSelectionBox)
            self.winOnThirdBtn.setObjectName("winOnThirdBtn")
            self.gridLayout.addWidget(self.winOnThirdBtn, 1, 3, 1, 1)
            self.winOnAllBtn = QtWidgets.QPushButton(self.answerSelectionBox)
            self.winOnAllBtn.setObjectName("winOnAllBtn")
            self.gridLayout.addWidget(self.winOnAllBtn, 1, 1, 1, 1)
            self.verticalLayout_2.addWidget(self.answerSelectionBox)
            self.winOnAllBtn.setText('Win on all accounts')
            self.winOnHalfBtn.setText('Win on half accounts')
            self.winOnThirdBtn.setText('Win on third accounts')
            self.confirmToWinInput.setText('Confirm')

        def hide_ans_buttons(self):
            try:
                self.ans1.hide()
                self.ans2.hide()
                self.ans3.hide()
                self.ans12.hide()
                self.ans23.hide()
                self.ans13.hide()
                self.ans123.hide()
                self.extraLifeBtn.hide()
            except:
                try:
                    self.show_ans_buttons()
                    self.hide_ans_buttons()
                except:
                    print("Error")

        def hide_checkpoint_buttons(self):
            self.winOnAllBtn.hide()
            self.winOnHalfBtn.hide()
            self.winOnThirdBtn.hide()
            self.numToWinInput.hide()
            self.confirmToWinInput.hide()

        def countdown(self, secs):
            while secs:
                self.nextShowLabel.setText(str(secs))
                time.sleep(1)
                secs -= 1
            self.nextShowLabel.setText('0')


    class Grand(QtCore.QThread,QtWidgets.QMainWindow, Ui_HQWater):
        signal = QtCore.pyqtSignal(dict)

        def __init__(self):
            super(Grand, self).__init__()
            try:
                self.t = grand_token["token"]
                self.grand = grand_token
                self.q_id = 0
                self.a1_id = 0
                self.a2_id = 0
                self.a3_id = 0
                self.has_life = False
                self.checkpoint_id = ''
                self.alive = False
            except:
                traceback.print_exc()

        def connect(self):
            for msg in persist(self.ws.get(), min_wait=0, max_wait=0):
                if msg.name == 'ready':
                    # self.ws.send_json({"authToken": self.t, "broadcastId": self.ws.broadcast, "type": "subscribe"})
                    # self.ws.send_json({"chatVisible": 0, "authToken": self.t,
                    #                    "type": "chatVisibilityToggled"})
                    self.ws.send_json({"type": "subscribe", "gameType": "trivia"})
                    self.ws.send_json({"type": "chatVisibilityToggled", "chatVisible": 0})
                    self.signal.emit({'act': 'connected_account', 'alive': True, 'self': self})
                    self.alive = True
                elif msg.name == 'text':
                    try:
                        data = json.loads(msg.text)
                        if data['type'] == 'question':
                            self.q_id = data['questionId']
                            self.a1_id = data['answers'][0]['answerId']
                            self.a2_id = data['answers'][1]['answerId']
                            self.a3_id = data['answers'][2]['answerId']
                            def answers(ans_id):
                                return data['answers'][ans_id]['text']
                            self.signal.emit(
                                {'act': 'question', 'question_text': str(data['question']), 'ans1': answers(0),
                                 'ans2': answers(1),
                                 'ans3': answers(2), 'q_id': self.q_id, 'a_id': [self.a1_id, self.a2_id, self.a3_id],
                                 'questionNumber':data['questionNumber']})
                        elif data['type'] == 'questionClosed':
                            self.signal.emit({'act': 'question_end'})
                        elif data['type'] == 'streak':
                            self.signal.emit({'act': 'streak', 'streak_count':data['current']})
                        elif data['type'] == 'questionSummary':
                            print(data['youGotItRight'])
                            for ans_id, answer in enumerate(data['answerCounts']):
                                if answer['correct']:
                                    try:
                                        ans = answer['answer']
                                    except KeyError:
                                        ans = answer['text']
                                    correct_ans = ans_id
                            self.signal.emit({'act': 'question_summary', 'correct_answer': correct_ans, 'text': ans,
                                              'advancingPlayersCount': data['advancingPlayersCount'] ,
                                              'eliminatedPlayersCount':data['eliminatedPlayersCount']})
                            if data['youGotItRight']:
                                self.signal.emit({'act': 'account_status', 'alive': True,
                                                  'can_use_life': True if self.has_life else False, 'self': self})
                                self.alive = True
                            else:
                                self.signal.emit({'act': 'account_status', 'alive': False,
                                                  'can_use_life': True if self.has_life else False, 'self': self})
                                self.alive = False
                        elif data['type'] == 'gameStatus':
                            try:
                                if data['extraLivesRemaining'] != 0:
                                    self.has_life = True
                                    self.signal.emit({'act': 'has_life', 'self': self})
                                elif not data['inTheGame']:  # account is eliminated
                                    self.signal.emit(
                                        {'act': 'account_status', 'can_use_life': True if self.has_life else False,
                                         'alive': False, 'self': self})
                                    self.alive = False
                            except KeyError:
                                pass
                        elif data['type'] == 'checkpoint':
                            self.checkpoint_id = data['checkpointId']
                            self.signal.emit({'act': 'checkpoint', 'offered_prize': data['prizeOffered'],
                                              'checkpoint_id': data['checkpointId']})
                        elif data['type'] == 'checkpointSummary':
                            self.signal.emit({'act': 'checkpoint_end'})
                    except Exception as e:
                        print(e)
                        pass

        def run(self):
            # self.api.easter_egg()
            if grand_token["proxy"] == "" or grand_token["proxy"] is None:
                self.api = HQApi(self.t, version="1.49.8")
            else:
                self.api = HQApi(self.t, proxy=grand_token["proxy"], version="1.49.8")
            try:
                self.ws = HQWebSocket(self.api, demo=False)
                try:
                    self.api.easter_egg()
                except:
                    pass
            except:
                self.ws = HQWebSocket(self.api, demo=True)

            self.connect()

        def close(self):
            return self.ws.close()

        def send_ans(self, a_id, q_id):
            if self.alive:
                try:
                    self.ws.send_answer(a_id, q_id)
                except:
                    self.connect()
                    self.ws.send_answer(a_id, q_id)

        def send_life(self):
            if self.has_life and not self.alive:
                self.ws.send_life(self.q_id)
                self.signal.emit({'act': 'life_used', 'self': self})
                self.has_life = False
                self.alive = True

        def send_check(self):
            try:
                if self.alive:
                    self.ws.checkpoint(winNow=True, checkpointId=self.checkpoint_id)
                    self.signal.emit({'act': 'checkpoint_use', 'self': self})
                    self.alive = False
            except:
                print(
                    'An error occured while sending the checkpoint, account is eliminated, pray for the money to come :/')
                self.signal.emit({'act': 'checkpoint_use', 'self': self})


    class HQ(QtCore.QThread):
        signal = QtCore.pyqtSignal(dict)

        def __init__(self, token):
            super(HQ, self).__init__()
            self.t = token

            self.q_id = 0
            self.a1_id = 0
            self.a2_id = 0
            self.a3_id = 0
            self.has_life = False
            self.checkpoint_id = ''
            self.alive = False

        def connect(self):
            for msg in persist(self.ws.get(), min_wait=0, max_wait=0):
                if msg.name == 'ready':
                    # self.ws.send_json({"authToken": self.t, "broadcastId": self.ws.broadcast, "type": "subscribe"})
                    # self.ws.send_json({"chatVisible": 0, "authToken": self.t,
                    #                    "type": "chatVisibilityToggled"})
                    self.ws.send_json({"type": "subscribe", "gameType": "trivia"})
                    self.ws.send_json({"type": "chatVisibilityToggled", "chatVisible": 0})
                    self.signal.emit({'act': 'connected_account', 'alive': True, 'self': self})
                    self.alive = True
                elif msg.name == 'text':
                    try:
                        data = json.loads(msg.text)
                        if data['type'] == 'question':
                            self.q_id = data['questionId']
                            self.a1_id = data['answers'][0]['answerId']
                            self.a2_id = data['answers'][1]['answerId']
                            self.a3_id = data['answers'][2]['answerId']

                        elif data['type'] == 'questionSummary':
                            print(data['youGotItRight'])
                            if data['youGotItRight']:
                                self.signal.emit({'act': 'account_status', 'alive': True,
                                                  'can_use_life': True if self.has_life else False, 'self': self})
                                self.alive = True
                            else:
                                self.signal.emit({'act': 'account_status', 'alive': False,
                                                  'can_use_life': True if self.has_life else False, 'self': self})
                                self.alive = False
                        elif data['type'] == 'gameStatus':
                            try:
                                if data['extraLivesRemaining'] != 0:
                                    self.has_life = True
                                    self.signal.emit({'act': 'has_life', 'self': self})
                                elif not data['inTheGame']:  # account is eliminated
                                    self.signal.emit(
                                        {'act': 'account_status', 'can_use_life': True if self.has_life else False,
                                         'alive': False, 'self': self})
                                    self.alive = False
                            except KeyError:
                                pass
                    except:
                        pass

        def run(self):
            # self.api.easter_egg()
            if self.t["proxy"] == "" or self.t["proxy"] is None:
                self.api = HQApi(self.t["token"], version="1.49.8")
            else:
                self.api = HQApi(self.t["token"], proxy=self.t["proxy"], version="1.49.8")
            try:
                self.ws = HQWebSocket(self.api, demo=False)
                try:
                    self.api.easter_egg()
                except:
                    pass
            except:
                self.ws = HQWebSocket(self.api, demo=True)

            self.connect()

        def close(self):
            return self.ws.close()

        def send_ans(self, a_id, q_id):
            if self.alive:
                try:
                    self.ws.send_answer(a_id, q_id)
                except:
                    self.connect()
                    self.ws.send_answer(a_id, q_id)

        def send_life(self):
            if self.has_life and not self.alive:
                try:
                    self.ws.send_life(self.q_id)
                    self.signal.emit({'act': 'life_used', 'self': self})
                    self.has_life = False
                    self.alive = True
                except:
                    self.connect()
                    self.ws.send_life(self.q_id)
                    self.signal.emit({'act': 'life_used', 'self': self})
                    self.has_life = False
                    self.alive = True

        def send_check(self):
            try:
                if self.alive:
                    self.ws.checkpoint(winNow=True, checkpointId=self.checkpoint_id)
                    self.signal.emit({'act': 'checkpoint_use', 'self': self})
                    self.alive = False
            except:
                print(
                    'An error occured while sending the checkpoint, account is eliminated, pray for the money to come :/')
                self.signal.emit({'act': 'checkpoint_use', 'self': self})


    class Main(QtWidgets.QMainWindow, Ui_HQWater):
        def __init__(self):
            global proxy, all_tokens
            super().__init__()
            self.MainWindow = QtWidgets.QMainWindow()
            self.ui = Ui_HQWater()
            self.ui.setupUi(self.MainWindow)
            self.ui.tableWidget.viewport().installEventFilter(self)
            self.ui.tableWidget.setSortingEnabled(True)
            self.ui.tableWidget.setColumnCount(6)
            self.ui.tableWidget.setHorizontalHeaderLabels(
                [self.tr("Nickname"), self.tr("Lifes"), self.tr("Total money"),
                 self.tr("On account"), self.tr("Banned"),self.tr("Token")])
            self.ui.tableWidget.resizeColumnsToContents()
            self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.ui.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
            self.ui.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.ui.tableWidget.viewport().installEventFilter(self)
            self.MainWindow.show()
            self.api = HQApi(grand_token["token"], proxy=grand_token["proxy"])
            self.row = 0  # Stuff for account checker
            self.thread_list = []  # All threads, even those not alive
            self.alive_threads = []  # Threads in the game
            self.threads = []  # Threads for account checker
            self.accounts_with_life = []  # Threads that have an extra life
            self.q_active = False
            self.checkpoint_active = False
            self.connected = False
            self.show = self.api.get_show()
            if self.show['active']:
                self.ui.nextShowLabel.setText('Show is Active')
            else:
                self.ui.nextShowLabel.setText(
                    '{}\n{}'.format(datetime.datetime.strptime(self.show['nextShowTime'][5:7]+self.show['nextShowTime'][8:10], "%m%d").strftime("%B %d")+' '+str(int(self.show['nextShowTime'][11:13])+3)+':'+self.show['nextShowTime'][14:16], self.show['nextShowPrize']))
            self.ui.aliveAccountsLabel.setText('Alive accounts')
            self.ui.connectButton.clicked.connect(self.connect_button)
            self.q_id = 0
            self.a1_id = 0
            self.a2_id = 0
            self.a3_id = 0
            self.to_remove = []
            self.accounts = []
            for t in all_tokens:
                c = Checker(t)
                c.signal.connect(self.checker)
                c.start()
                self.threads.append(c)
            self.ui.tableWidget.viewport().update();
        def eventFilter(self, source, event):
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                self.select()
            return super(Main, self).eventFilter(source, event)

        def popup(self, callback_ok, label: str = "", title: str = "HQWater", w: int = 500,
                  h: int = 100) -> None:
            dlg = QInputDialog(self)
            dlg.setInputMode(QInputDialog.TextInput)
            dlg.setLabelText(label)
            dlg.setWindowTitle(title)
            dlg.resize(w, h)
            ok = dlg.exec_()
            text = dlg.textValue()
            if ok == 1:
                callback_ok(text)
                return
            pass

        def select(self):
            try:
                self.row = self.ui.tableWidget.currentItem().row()
            except AttributeError:
                return
            self.popup(self.cashout, "Your PayPal email to cashout:", "Cashout")

        def cashout(self, mail):
            global all_tokens
            proxy = None
            hq = HQApi(self.ui.tableWidget.selectedItems()[5].text(), proxy=proxy)
            try:
                cash = hq.make_payout(mail)
            except Exception as e:
                cash = e
            print(cash)
            alert("Cashout response", str(cash))

        def recreate_accounts(self):
            for i in range(len(self.accounts)):
                self.ui.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(self.accounts[i]["nickname"]))
                self.ui.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(self.accounts[i]["lifes"])))
                self.ui.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(str(self.accounts[i]["money_all"])))
                self.ui.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(str(self.accounts[i]["money_un"])))
                self.ui.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(str(self.accounts[i]["ban"])))
                self.ui.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem(self.accounts[i]["token"]))
            self.ui.tableWidget.setRowCount(len(self.accounts))

        def checker(self, dict):
            self.accounts.append(dict)
            self.recreate_accounts()
            self.recreate_accounts()

        def handler(self, dict):
            if dict['act'] == 'question':
                self.ui.questionNumberLabel.setText("Question № "+str(dict['questionNumber']))
                self.question_time = time.time()
                self.show_ans_buttons()
                self.q_active = True
                countdown = Thread(target=self.ui.countdown, args={10})
                countdown.start()
                self.ui.questionLabel.setText(dict['question_text'])
                self.ui.variant1.setText(dict['ans1'])
                self.ui.variant2.setText(dict['ans2'])
                self.ui.variant3.setText(dict['ans3'])
                self.q_id = dict['q_id']
                self.a1_id = dict['a_id'][0]
                self.a2_id = dict['a_id'][1]
                self.a3_id = dict['a_id'][2]
                # self.send("123")
            elif dict['act'] == 'streak':
                self.ui.streakLabel.setText('Streak: '+str(dict['streak_count']))
            elif dict['act'] == 'account_status':
                if not dict['alive'] and dict['self'] in self.alive_threads:
                    try:
                        self.alive_threads.remove(dict['self'])
                    except:
                        print("ERROR DELETE")
                    if dict["can_use_life"]:
                        if dict["self"] not in self.accounts_with_life:
                            self.accounts_with_life.append(dict["self"])
                    self.ui.aliveAccountsLabel.setText(
                        str(len(self.alive_threads)) + ' accounts||awl ' + str(len(self.accounts_with_life)))
                elif dict['self'] not in self.alive_threads and dict['alive']:
                    self.alive_threads.append(dict['self'])
                    self.ui.aliveAccountsLabel.setText(
                        str(len(self.alive_threads)) + ' accounts||awl ' + str(len(self.accounts_with_life)))
            elif dict['act'] == 'question_summary':
                self.ui.correctLabel.setText("Correct: "+str(dict['advancingPlayersCount'])+" InCorrect: "+str(dict['eliminatedPlayersCount']))
                for thread in self.thread_list:
                    if not thread.alive and thread in self.alive_threads:
                        self.alive_threads.remove(thread)
                    if thread.alive and thread not in self.alive_threads:
                        self.alive_threads.append(thread)
                self.show_ans_buttons()
                if dict['correct_answer'] == 0:
                    self.ui.variant1.setText(dict['text'] + ' - ✔')
                elif dict['correct_answer'] == 1:
                    self.ui.variant2.setText(dict['text'] + ' - ✔')
                elif dict['correct_answer'] == 2:
                    self.ui.variant3.setText(dict['text'] + ' - ✔')
            elif dict['act'] == 'connected_account':
                if dict['self'] not in self.alive_threads:
                    self.alive_threads.append(dict['self'])
                self.ui.aliveAccountsLabel.setText(
                    str(len(self.alive_threads)) + ' accounts||awl ' + str(len(self.accounts_with_life)))
            elif dict['act'] == 'question_end':
                self.ui.hide_ans_buttons()
                self.q_active = False
                self.ui.nextShowLabel.setText('Question ended')
            elif dict['act'] == 'has_life':
                if dict["self"] not in self.accounts_with_life:
                    self.accounts_with_life.append(dict['self'])
                self.ui.aliveAccountsLabel.setText(
                    str(len(self.alive_threads)) + ' accounts||awl ' + str(len(self.accounts_with_life)))
            elif dict['act'] == 'checkpoint':
                countdown = Thread(target=self.ui.countdown, args={10})
                countdown.start()
                self.checkpoint_active = True
                self.ui.questionLabel.setText('Checkpoint')
                self.ui.variant1.setText('-' * 100)
                self.ui.variant2.setText('Offered prize ' + dict['offered_prize'])
                self.ui.variant3.setText('-' * 100)
                self.ui.hide_ans_buttons()
                self.show_checkpoint_buttons()
            elif dict['act'] == 'checkpoint_end':
                for account in self.to_remove:
                    try:
                        self.alive_threads.remove(account)
                    except:
                        pass
                    self.ui.aliveAccountsLabel.setText(
                        str(len(self.alive_threads)) + ' accounts||awl ' + str(len(self.accounts_with_life)))
                self.to_remove = []
                self.checkpoint_active = False
                try:
                    self.ui.hide_checkpoint_buttons()
                except:
                    print("Error while hiding checkpoint buttons")
                self.ui.hide_ans_buttons()
            elif dict['act'] == 'checkpoint_use':
                if dict['self'] in self.alive_threads:
                    self.to_remove.append(dict["self"])
            elif dict["act"] == "life_used":
                if dict['self'] not in self.alive_threads:
                    self.alive_threads.append(dict['self'])
                if dict["self"] in self.accounts_with_life:
                    self.accounts_with_life.remove(dict["self"])
                self.ui.aliveAccountsLabel.setText(
                    str(len(self.alive_threads)) + ' accounts||awl ' + str(len(self.accounts_with_life)))

        def connect_button(self):
            if not self.connected:
                try:
                    self.ws = Grand()
                    self.ws.signal.connect(self.handler)
                    self.ws.start()
                    self.alive_threads.append(self.ws)
                    for token in tokens:
                        t = HQ(token)
                        t.signal.connect(self.handler)
                        self.thread_list.append(t)
                    for t in self.thread_list:
                        t.start()
                    self.ui.nextShowLabel.setText('Connected')
                    self.connected = True
                except:
                    traceback.print_exc()
        def send(self, ans):
            self.ui.hide_ans_buttons()
            sender_thread = Thread(target=self.split, args={ans})
            sender_thread.start()

        def split(self, ans):
            if self.connected and self.q_active:
                while time.time() - self.question_time < 10:
                    pass
                print("Sent answer")
                if ans == '1':
                    for thread in self.alive_threads:
                        thread.send_ans(self.a1_id, self.q_id)
                elif ans == '2':
                    for thread in self.alive_threads:
                        thread.send_ans(self.a2_id, self.q_id)
                elif ans == '3':
                    for thread in self.alive_threads:
                        thread.send_ans(self.a3_id, self.q_id)
                elif ans == '12':
                    if len(self.alive_threads) % 2 == 0:
                        select_one = self.alive_threads[:len(self.alive_threads) // 2]
                        select_two = self.alive_threads[len(self.alive_threads) // 2:]
                        for thread in select_one:
                            thread.send_ans(self.a1_id, self.q_id)
                        for thread in select_two:
                            thread.send_ans(self.a2_id, self.q_id)
                    elif len(self.alive_threads) % 2 == 1:
                        temp = self.alive_threads[-1]
                        self.alive_threads.pop()
                        select_one = self.alive_threads[:len(self.alive_threads) // 2]
                        select_two = self.alive_threads[len(self.alive_threads) // 2:]
                        select_one.append(temp)
                        for thread in select_one:
                            thread.send_ans(self.a1_id, self.q_id)
                        for thread in select_two:
                            thread.send_ans(self.a2_id, self.q_id)
                elif ans == '23':
                    if len(self.alive_threads) % 2 == 0:
                        select_two = self.alive_threads[:len(self.alive_threads) // 2]
                        select_three = self.alive_threads[len(self.alive_threads) // 2:]
                        for thread in select_two:
                            thread.send_ans(self.a2_id, self.q_id)
                        for thread in select_three:
                            thread.send_ans(self.a3_id, self.q_id)
                    elif len(self.alive_threads) % 2 == 1:
                        temp = self.alive_threads[-1]
                        self.alive_threads.pop()
                        select_two = self.alive_threads[:len(self.alive_threads) // 2]
                        select_three = self.alive_threads[len(self.alive_threads) // 2:]
                        select_two.append(temp)
                        for thread in select_two:
                            thread.send_ans(self.a2_id, self.q_id)
                        for thread in select_three:
                            thread.send_ans(self.a3_id, self.q_id)
                elif ans == '13':
                    if len(self.alive_threads) % 2 == 0:
                        select_one = self.alive_threads[:len(self.alive_threads) // 2]
                        select_three = self.alive_threads[len(self.alive_threads) // 2:]
                        for thread in select_one:
                            thread.send_ans(self.a1_id, self.q_id)
                        for thread in select_three:
                            thread.send_ans(self.a3_id, self.q_id)
                    elif len(self.alive_threads) % 2 == 1:
                        temp = self.alive_threads[-1]
                        self.alive_threads.pop()
                        select_one = self.alive_threads[:len(self.alive_threads) // 2]
                        select_three = self.alive_threads[len(self.alive_threads) // 2:]
                        select_one.append(temp)
                        for thread in select_one:
                            thread.send_ans(self.a1_id, self.q_id)
                        for thread in select_three:
                            thread.send_ans(self.a3_id, self.q_id)
                elif ans == '123':
                    if len(self.alive_threads) % 3 == 0:
                        select_one = self.split_list(self.alive_threads, 3)[0]
                        select_two = self.split_list(self.alive_threads, 3)[1]
                        select_three = self.split_list(self.alive_threads, 3)[2]
                        for thread in select_one:
                            thread.send_ans(self.a1_id, self.q_id)
                        for thread in select_two:
                            thread.send_ans(self.a2_id, self.q_id)
                        for thread in select_three:
                            thread.send_ans(self.a3_id, self.q_id)
                    elif len(self.alive_threads) % 3 == 1:
                        temp = self.alive_threads[-1]
                        self.alive_threads.pop()
                        select_one = self.split_list(self.alive_threads, 3)[0]
                        select_two = self.split_list(self.alive_threads, 3)[1]
                        select_three = self.split_list(self.alive_threads, 3)[2]
                        select_one.append(temp)
                        for thread in select_one:
                            thread.send_ans(self.a1_id, self.q_id)
                        for thread in select_two:
                            thread.send_ans(self.a2_id, self.q_id)
                        for thread in select_three:
                            thread.send_ans(self.a3_id, self.q_id)
                    elif len(self.alive_threads) % 3 == 2:
                        temp = self.alive_threads[-1]
                        temp2 = self.alive_threads[-2]
                        for i in range(2):
                            self.alive_threads.pop()
                        select_one = self.split_list(self.alive_threads, 3)[0]
                        select_two = self.split_list(self.alive_threads, 3)[1]
                        select_three = self.split_list(self.alive_threads, 3)[2]
                        select_one.append(temp)
                        select_two.append(temp2)
                        for thread in select_one:
                            thread.send_ans(self.a1_id, self.q_id)
                        for thread in select_two:
                            thread.send_ans(self.a2_id, self.q_id)
                        for thread in select_three:
                            thread.send_ans(self.a3_id, self.q_id)

        def split_list(self, lst, wanted_parts):
            length = len(lst)
            return [lst[i * length // wanted_parts: (i + 1) * length // wanted_parts]
                    for i in range(wanted_parts)]

        def send_life(self):
            self.ui.hide_ans_buttons()
            if not self.q_active:
                for thread in self.thread_list:
                    if thread not in self.alive_threads and thread.has_life and not thread.alive:
                        thread.send_life()
                        # self.alive_threads.append(thread)
                        print('Sent extra life', thread.t)
                        self.ui.aliveAccountsLabel.setText(
                            str(len(self.alive_threads)) + ' accounts||awl ' + str(len(self.accounts_with_life)))
                self.ws.send_life()

        def send_checkpoint(self, act):
            try:
                self.ui.hide_checkpoint_buttons()
                print('Sending checkpoint on {} accounts'.format(act))
                if self.checkpoint_active:
                    if act == 'all':
                        for thread in self.alive_threads:
                            thread.send_check()
                    elif act == 'half':
                        for thread in self.alive_threads[0:len(self.alive_threads) // 2]:
                            thread.send_check()
                    elif act == 'third':
                        for thread in self.alive_threads[0:len(self.alive_threads) // 3]:
                            thread.send_check()
                    else:
                        num = int(act())
                        print(num)
                        for i in range(num):
                            self.alive_threads[i].send_check()
            except:
                print('Error')

        def show_ans_buttons(self):
            self.ui.show_ans_buttons()
            self.ui.ans1.clicked.connect(partial(self.send, '1'))
            self.ui.ans2.clicked.connect(partial(self.send, '2'))
            self.ui.ans3.clicked.connect(partial(self.send, '3'))
            self.ui.ans12.clicked.connect(partial(self.send, '12'))
            self.ui.ans23.clicked.connect(partial(self.send, '23'))
            self.ui.ans13.clicked.connect(partial(self.send, '13'))
            self.ui.ans123.clicked.connect(partial(self.send, '123'))
            self.ui.extraLifeBtn.clicked.connect(self.send_life)

        def show_checkpoint_buttons(self):
            self.ui.show_checkpoint_buttons()
            self.ui.winOnAllBtn.clicked.connect(partial(self.send_checkpoint, 'all'))
            self.ui.winOnHalfBtn.clicked.connect(partial(self.send_checkpoint, 'half'))
            self.ui.winOnThirdBtn.clicked.connect(partial(self.send_checkpoint, 'third'))
            self.ui.confirmToWinInput.clicked.connect(partial(self.send_checkpoint, self.ui.numToWinInput.text))


    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        window = Main()
        apply_stylesheet(app, theme='dark_blue.xml')
        app.exec()
except:
    traceback.print_exc()
