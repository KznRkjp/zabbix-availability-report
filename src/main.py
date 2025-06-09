#!/usr/bin/python
# -*- coding: UTF8 -*-

import os
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from alive_progress import alive_bar
from dotenv import load_dotenv
from convert import json_to_csv

# --- Configuration ---
DATETIME_START = "2025-06-08 00:00" # Year-Month-Day Hour:Minute
DATETIME_END = "2025-06-08 01:00" # Year-Month-Day Hour:Minute
TIME_INTERVALS_TO_CHECK = 1

# --- Load environment variables ---
load_dotenv()
TOKEN = os.getenv('ZABBIX_TOKEN')
URL = os.getenv('ZABBIX_URL')
HEADERS = {
    'content-type': 'application/json-rpc',
    'Authorization': f'Bearer {TOKEN}'
}

def get_all_hosts() -> Dict[str, Any]:
    """Fetch all hosts from Zabbix."""
    print("Start")
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "inventory_mode", "name"],
            "selectInterfaces": ["interfaceid", "ip"],
            "selectInventory": ["location_lat", "location_lon", "location"]
        },
        "id": 2
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    now = datetime.now()
    filename = f"zabbix_hosts-{now:%y-%m-%d-%H-%M-%S}.json"
    with open(filename, 'w') as f:
        json.dump(response, f)
    return response

def get_icmpping_id(hostid: str) -> Optional[str]:
    """Get the item ID for ICMP ping for a given host."""
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": "extend",
            "hostids": hostid
        },
        "id": 1,
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    if 'error' in response:
        print("Error:", response['error'])
        return None
    for item in response.get('result', []):
        if item.get('key_') == "icmpping":
            return item.get('itemid')
    return None

def history_get(hostid: str, itemid: str, start: float, stop: float) -> float:
    """Get the availability ratio for a host's ICMP ping item in a time range."""
    payload = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "itemids": itemid,
            "hostids": hostid,
            "time_from": int(start),
            "time_till": int(stop)
        },
        "id": 1,
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    try:
        results = response.get('result', [])
        if not results:
            return 0.0
        available = sum(1 for i in results if i.get('value') == '1')
        return available / len(results)
    except Exception:
        return 0.0

def main() -> None:
    """Main execution function."""
    results: List[Dict[str, Any]] = []
    hosts = get_all_hosts()
    host_list = hosts.get('result', [])
    with alive_bar(len(host_list)) as bar:
        for host in host_list:
            dt1 = datetime.strptime(DATETIME_START, "%Y-%m-%d %H:%M")
            dt2 = datetime.strptime(DATETIME_END, "%Y-%m-%d %H:%M")
            bar()
            subresult = {
                'host': host['host'],
                'hostid': host['hostid'],
                'icmp_id': get_icmpping_id(host['hostid'])
            }
            for _ in range(TIME_INTERVALS_TO_CHECK):
                if subresult['icmp_id']:
                    key = dt1.strftime("%Y-%m-%d %H:%M")
                    subresult[key] = history_get(subresult['hostid'], subresult['icmp_id'], dt1.timestamp(), dt2.timestamp())
                dt1 += timedelta(days=1)
                dt2 += timedelta(days=1)
            results.append(subresult)
    now = datetime.now()
    filename = f"zabbix_availability-{now:%y-%m-%d-%H-%M-%S}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    csv_filename = f"zabbix_availability-{now:%y-%m-%d-%H-%M-%S}.csv"
    json_to_csv(filename, csv_filename)

if __name__ == "__main__":
    main()
