import subprocess
import time
import frida

from flask import Flask

app = Flask(__name__)

token = None
nonce = None
busy = False
device = frida.get_usb_device()


@app.route('/generate_fcm', methods=['GET', 'POST'])
def generate():
    global token, nonce, busy, device
    while busy:
        pass
    try:
        t = time.time()
        busy = True
        token = None

        def message_handler(message, *args):
            global token
            token = message['payload']

        while not token:
            subprocess.Popen(['adb', '-d', 'shell', 'pm', 'clear', 'com.intermedia.hq'])
            time.sleep(2)
            pid = device.spawn(["com.intermedia.hq"])
            device.resume(pid)
            time.sleep(1)
            session = device.attach(pid)

            with open("hook.js") as f:
                script = session.create_script(f.read())
            script.on("message", message_handler)
            script.load()

            time.sleep(5)
            temp_token = token
            busy = False
            token = None
            return {"token": temp_token, "time": time.time() - t}
    except Exception as e:
        print(e)
        busy = False
        return "Fail", 500


if __name__ == '__main__':
    app.run()
