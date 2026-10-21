import requests

def get_ip_geolocation(ip_address):
  r = requests.get(f"http://ip-api.com/json/{ip_address}")
  return r.json()