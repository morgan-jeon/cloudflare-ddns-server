import requests, json
import socket
import secrets

CF_GLOBAL_KEY = secrets.cloudflare.global_key
CF_API_KEY = secrets.cloudflare.api_key
CF_EMAIL = secrets.cloudflare.email
zone_id = secrets.cloudflare.zone_id

auth = {
		"X-Auth-Email": CF_EMAIL,
		"X-Auth-Key": CF_GLOBAL_KEY,
		"Content-Type": "application/json"
}

def check_available(domain):
	base_domian = ".".join(domain.split(".")[-2:])
	print(base_domian)

	if base_domian in zone_id.keys():
		return base_domian
	else:
		return 0

def update_dns(domain, new_ip):
	base_domian = check_available(domain)
	assert base_domian
	print(domain)
	zid = zone_id[base_domian]
	list_api = f"https://api.cloudflare.com/client/v4/zones/{zid}/dns_records?name="
	edit_api = f"https://api.cloudflare.com/client/v4/zones/{zid}/dns_records"
	dns_info = {"type": "A", "name": domain, "ttl": 3600, "proxied": False}

	check_domain(zid, domain, new_ip)

	try:
		old_ip = socket.gethostbyname(dns_info["name"])
	except:
		old_ip = None

	if old_ip == new_ip:
		print(f"No change. {dns_info['name']}: {old_ip}")
		return 0

	else:
		dns_res_txt = requests.get(f"{list_api}{domain}", headers=auth).text
		print(dns_res_txt)
		dns_id = json.loads(dns_res_txt)["result"][0]["id"]
		dns_info["content"] = new_ip
		upd = requests.put(f"{edit_api}/{dns_id}", headers=auth, data=json.dumps(dns_info)).text
	 
		try:
			upd = json.loads(upd)
		except:
			print(upd)

		dn_name = upd["result"]["name"]
		dn_type = upd["result"]["type"]
		dn_content = upd["result"]["content"]

		print(f"DNS record updated to {dn_type}: {dn_name} = {dn_content}")
		return f"Success: {dn_name} updated to {dn_content}"

def check_domain(zid, domain, ip = None):
	existing = [ i["name"] for i in list_domains(zid)]
	print(existing, domain)

	if domain not in existing:
		create_record(domain, zid, ip)

def create_record(sub, zid, ip = "1.1.1.1", record = "A"):
	print(f"create_record({sub}, {zid}, {ip}, {record})")
	api_url = f"https://api.cloudflare.com/client/v4/zones/{zid}/dns_records"
	data = {
		"content": ip,
		"name": sub,
		"proxied": False,
		"type": record,
		"comment": "",
		"ttl": 3600
	}
	res_txt = requests.post(api_url, headers=auth, data=json.dumps(data)).text
	print(res_txt)
	return res_txt

def list_domains(zid):
	api_url = f"https://api.cloudflare.com/client/v4/zones/{zid}/dns_records"
	return json.loads(requests.get(api_url, headers=auth).text)["result"]

if __name__=="__main__":
	if len(sys.argv) not in [3, 2]:
		print("cfddns.py [domain] (ip)")
	this_domain = sys.argv[2]
	if len(sys.argv) == 2:
		this_ip = json.loads(requests.get("https://ip4.seeip.org/json").text)["ip"]
	else:
		this_ip = sys.argv[3]
	print(this_ip, this_domain)
	update_dns(this_domain, this_ip)
