import requests
import json
from ipaddress import ip_address
TOKEN = 'iplocation.net'

def ip_to_location(ip):
    if type(ip) == str:
        try:
            ip_address(ip)
        except ValueError:
            return 'Not a valid IP'
        except Exception as e:
            return 'Unknown error %s' % (str(e))
        else:
            data = requests.get('http://ipinfo.io/%s/json?token=iplocation.net' % (ip,))
            location_dict = json.loads(data.text)
            return location_dict
    else:
        return 'Function accepts only string of ip eg: 106.51.254.182'

if __name__ == '__main__':
    ip_to_location('106.51.254.182')

