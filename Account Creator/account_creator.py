import sqlite3
import time
import uuid
import requests
from HQApi import HQApi
from faker import Faker

with open("api_key.txt") as f:
	SMSHUB_API_KEY=f.read()
API_ENDPOINT = "https://sms-activate.ru/stubs/handler_api.php?"

ACCOUNTS_PER_IP = 3

with open("proxy.txt") as f:
    proxy = f.read().split("\n")
for prx in proxy:
    PROXY = "https://" + prx
    for i in range(ACCOUNTS_PER_IP):

        code = None
        SMS_ARRIVED = False
        def get_sms():
            global api, send_sms, code
            get_number = requests.get(
                API_ENDPOINT + "api_key=%s&action=getNumber&service=kp&country=12" % SMSHUB_API_KEY).text.split(
                ":")
            while get_number[0]=="NO_NUMBERS" or "</title>" in get_number[1]:
                get_number = requests.get(
                    API_ENDPOINT + "api_key=%s&action=getNumber&service=kp&country=12" % SMSHUB_API_KEY).text.split(
                    ":")
            number = "+" + get_number[2]
            activation_id = get_number[1]
            print("Got this phone number", number, "activation id is", activation_id)
            api = HQApi(proxy=PROXY, version="1.49.8")
            send_sms = api.send_code(number)
            requests.get(
                API_ENDPOINT + "api_key=" + SMSHUB_API_KEY + "&action=setStatus&status=1&id=" + activation_id)
            print(send_sms)
            code = None
            t = time.time()
            while code is None:
                if time.time() - t > 40:
                    print("Sms did not arrive, getting new number")
                    requests.get(
                        API_ENDPOINT + "api_key=%s&action=setStatus&status=%s&id=%s" % (
                            SMSHUB_API_KEY, "8", activation_id))
                    break
                r = requests.get(
                    API_ENDPOINT + "api_key=%s&action=getStatus&id=%s" % (
                        SMSHUB_API_KEY, activation_id))
                if "STATUS_OK" in r.text:
                    code = r.text.split(":")[1]
                    print("Got this sms code", code)
                    requests.get(
                        API_ENDPOINT + "api_key=%s&action=setStatus&status=%s&id=%s" % (
                            SMSHUB_API_KEY, "6", activation_id))


        while code is None:
            get_sms()

        api.confirm_code(send_sms["verificationId"], int(code))
        name_found = False
        while not name_found:
            fake = Faker()
            name = fake.simple_profile()["username"]
            kek = ""
            for s in name:
                kek += s
                try:
                    api.check_username(kek)
                    if kek == name:
                        name_found = True
                except:
                    pass
        token = api.register(send_sms["verificationId"], name)
        print(token)

        db = sqlite3.connect("hqwater.db")
        cursor = db.cursor()
        sql = "INSERT INTO accounts VALUES(?,?,?,?,?)"
        val = (token["accessToken"], PROXY, "", token["loginToken"], token["authToken"])
        cursor.execute(sql, val)
        db.commit()
        api = HQApi(proxy=PROXY, token=token["accessToken"])
        try:
            api.season_xp()
        except:
            pass
        config = api.config()
        print(config["redEnigma"], config["nonce"])
        devicetoken = requests.get("http://localhost:5000/generate_fcm").json()
        while devicetoken["token"] is None:
            devicetoken = requests.get("http://localhost:5000/generate_fcm").json()

        api.register_device_token(devicetoken)
        print("done")