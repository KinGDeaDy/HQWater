import subprocess
import time
import frida
from flask import Flask, request

app = Flask(__name__)

token = None
nonce = None
busy = False
fcm_token = None
fcm_nonce = None
fcm_busy = False
fcm_device = frida.get_usb_device()
import os, signal

@app.route('/safetynet', methods=['POST'])
def generate_nonce():
    global token, nonce, busy
    content = request.get_json(silent=True)
    while busy:
        pass
    try:
        t = time.time()
        busy = True
        nonce = content['nonce']
        mitm = subprocess.Popen(["mitmdump", "-s", "mitm.py"], shell=True)
        subprocess.run(["adb", "-d", "shell", "sleep", "5"])
        subprocess.run(["adb", "-d", "shell", "am", "force-stop", "com.intermedia.hq"])
        subprocess.run(
            ["adb", "-d", "shell", "monkey", "-p", "com.intermedia.hq", "-c", "android.intent.category.LAUNCHER", "1"])
        while not token:
            pass
        busy = False
        nonce = None
        mitm.kill()
        # os.killpg(os.getpgid(mitm.pid), signal.SIGTERM)
        temp_token = token
        token = None
        return {"token": temp_token, "time": time.time() - t}
    except:
        busy = False
        return "Fail", 500


@app.route('/put', methods=['POST'])
def put():
    global token
    token = [*request.form.to_dict()][0].split('"token": "')[1].split('"}')[0].replace("/", "")
    return "OK"


@app.route('/nonce')
def get():
    global nonce
    return nonce


@app.route('/generate_fcm', methods=['GET', 'POST'])
def generate_fcm():
    global fcm_token, fcm_nonce, fcm_busy, fcm_device
    while fcm_busy:
        pass
    try:
        t = time.time()
        fcm_busy = True
        fcm_token = None

        def message_handler(message, *args):
            global fcm_token
            fcm_token = message['payload']

        while not fcm_token:
            subprocess.Popen(['adb', '-e', 'shell', 'pm', 'clear', 'com.intermedia.hq'])
            time.sleep(2)
            pid = fcm_device.spawn(["com.intermedia.hq"])
            fcm_device.resume(pid)
            time.sleep(5)
            session = fcm_device.attach(pid)

            with open("./HQ FCM Hook/hook.js") as f:
                script = session.create_script(f.read())
            script.on("message", message_handler)
            script.load()

            time.sleep(5)
            temp_token = fcm_token
            fcm_busy = False
            fcm_token = None
            return {"token": temp_token, "time": time.time() - t}
    except Exception as e:
        print(e)
        fcm_busy = False
        return "Fail", 500


if __name__ == '__main__':
    app.run()
