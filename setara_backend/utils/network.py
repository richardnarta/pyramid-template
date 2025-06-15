import json
import requests


def get_location_from_ip(ip_address):
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        response.raise_for_status()
        data = response.json()
        return {
            'city': data.get('city'),
            'loc': data.get('loc')
        }
    except Exception as e:
        return {
            'city': None,
            'loc': None
        }
