# Zabbix Availability Report

This project generates availability reports for Zabbix-monitored hosts by querying the Zabbix API for ICMP ping (availability) data and exporting the results to CSV and JSON files.
Tested on Zabbix 7.2 but should work on other versions as well.
Zabbix built in availability report is slow, can't be date specific and if you have more than 2k hosts and want satistics for a week ore more will never execute. 

## Features

- Fetches all hosts from Zabbix with inventory and interface details.
- Retrieves ICMP ping item IDs for each host.
- Calculates host availability ratios over a specified time range.
- Exports results to JSON and CSV for further analysis.

## Requirements

- Python 3.8+
- Zabbix API access (token and URL)
- [requests](https://pypi.org/project/requests/)
- [alive-progress](https://pypi.org/project/alive-progress/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

You should get zabbix api token from your zabbix server.

[Here is the link to the manual](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/users/api_tokens)

Set your Zabbix API token and URL in a `.env` file (rename .env.example to .env):

```
ZABBIX_TOKEN=your_zabbix_api_token
ZABBIX_URL=https://your.zabbix.server/api_jsonrpc.php
```

Edit `src/main.py` to adjust the time range and intervals.

For example, this will create 2 columns: `2025-06-08 00:00` and `2025-06-09 00:00`.
Each column shows availability for the 00:00–01:00 interval on that date.

`TIME_INTERVALS_TO_CHECK` is responsible for the number of intervals; they grow by day starting from `DATETIME_START`/`DATETIME_END`.
`DATETIME_START` - start of interval
`DATETIME_END` - end of interval

```python
DATETIME_START = "2025-06-08 00:00"  # Year-Month-Day Hour:Minute
DATETIME_END = "2025-06-08 01:00"  # Year-Month-Day Hour:Minute
TIME_INTERVALS_TO_CHECK = 2
```

## Usage

Run the main script:

```bash
python3 src/main.py
```

Quick start (minimal):

```bash
cp .env.example .env
# Edit .env with real values for ZABBIX_TOKEN and ZABBIX_URL
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/main.py
```

This will:

- Query Zabbix for hosts and their ICMP ping data.
- Calculate availability for each host in the specified time range.
- Save results as `zabbix_availability-YY-MM-DD-HH-MM-SS.json` and `.csv`.

## Output Example

A sample CSV output (`zabbix_availability-25-06-09-12-24-58.csv`):

```
host,hostid,icmp_id,2025-06-08 00:00,2025-06-09 00:00
HOST-4014431.1,14354,60538,0.9,0.95
HOST-5913081.1,14355,60541,0.08333333333333333,0.12
HOST-6014367.1,14201,60079,0.9666666666666667,0.98
...
```

- `host`: Host name in Zabbix
- `hostid`: Zabbix host ID
- `icmp_id`: ICMP ping item ID
- `2025-06-08 00:00`: Availability ratio for the specified interval (1.0 = 100% up, 0.0 = 0% up)

## Customization

- Adjust the time range and intervals in `main.py` as needed.
- Extend the script to include more item types or metrics.

## License

MIT License

---

**Example:**

To generate a report run:

```bash
python3 src/main.py
```

Check the generated CSV for host availability ratios.