import requests, json

# 记录用户数据
def save_log(user_ip, text):
	url = ("http://freegeoip.net/json/%s" %user_ip)
	r = requests.get(url)
	ip_info = json.loads(r.text)
	country = ip_info['country_name']
	region = ip_info['region_name']
	city = ip_info['city']
	# 保存文件
	with open("va.log", 'a', encoding='utf-8') as fd:
		log = ("User IP: %s, Country: %s, Region: %s, City: %s\n\n"
		       %(user_ip, country, region, city))
		log += text + "\n\n"
		fd.write(log)