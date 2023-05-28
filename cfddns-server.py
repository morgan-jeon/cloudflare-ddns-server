from fastapi import FastAPI, Request
import cfddns
import requests
import secrets

app = FastAPI()

def cloudflare(ip, domain):
		return cfddns.update_dns(domain, ip)

def njalla(ip, domain, key = None):
	if not key:
		return 0
	return requests.get(f"https://njal.la/update/?h={domain}&k={key}&a={ip}").text

def route_ddns(provider, sub, domain, ip, sk = None):
	if provider not in ddns_func:
		return 0
	return ddns_func[provider](ip, domain, sk)

ddns_func = {"cloudflare": cloudflare, 
			"njalla": njalla}

@app.get ("/update")
async def ddns ( request: Request, sub: str, a: str | None = None, k: str | None = None, auto: bool | None = None, sk: str | None = None ):
	print(f"Request from {request.client.host} with [ sub: {sub}, a: {a}, k: {k}, auto: {auto}, sk: {sk} ]")

	if k not in key_dict.values():
		return "Error: Key not authorized"

	for i in key_dict:
		if key_dict[i] == k:
			domain = i
			break

	if auto:
		ip = request.client.host
		result = route_ddns(sub, domain, ip, sk)
	else:
		result = route_ddns(sub, domain, a, sk)

	if not result:
		return "Error"
	else:
		return result