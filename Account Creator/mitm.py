import urllib.request
import urllib.parse
from mitmproxy import http
import json

nonce = urllib.request.urlopen('http://127.0.0.1:5000/nonce').read().decode()
print("Running for nonce:", nonce)


def request(flow: http.HTTPFlow) -> None:
    if flow.request.pretty_url == "https://api-quiz.hype.space/config":
        flow.response = http.HTTPResponse.make(
            200,
            json.dumps({
                "redEnigma": True,
                "nonce": nonce,
            }).encode(),
            {"Content-Type": "application/json; charset=utf-8"}
        )
    elif flow.request.pretty_url == "https://api-quiz.hype.space/red-enigma/android":
        print("Captured SafetyNet response")
        js = json.loads(flow.request.data.content.decode())
        data = json.dumps(js)
        data = str(data)
        data = data.encode('utf-8')
        req = urllib.request.Request('http://127.0.0.1:5000/put', data=data)
        resp = urllib.request.urlopen(req)
        flow.kill()
    elif flow.request.pretty_url.startswith('https://api-quiz.hype.space/'):
        flow.response = http.HTTPResponse.make(
            200,
            json.dumps({"pwned_by": "Lapkioff"}).encode(),
            {"Content-Type": "application/json; charset=utf-8"}
        )
