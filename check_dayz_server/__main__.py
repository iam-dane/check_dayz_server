"""
CLI entrypoint
"""
import argparse
import ipaddress
import os
import sys
import time


import dotenv
import requests
from tabulate import tabulate


dotenv.load_dotenv()


SERVER_KEYS = [
    'name',
    'players',
]

class IPPort:

    def __init__(self, value: str):
        self.value = value
        self.ip = format(ipaddress.ip_address(value.split(':')[0]))
        self.port = int(value.split(':')[1])
    
    def __str__(self):
        return self.value

    def ip(self):
        return self.ip

    def port(self):
        return self.port


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'ip_port',
        metavar='IP:PORT',
        type=IPPort,
        help='Example: 85.190.157.113:10200')
    parser.add_argument(
        '--steam-api-key',
        dest='steam_api_key',
        metavar='KEY',
        default='',
    )
    parser.add_argument(
        '--table-format',
        dest='table_format',
        metavar='FORMAT',
        default='simple',
        choices=[
            'plain',
            'simple',
            'github',
            'grid',
            'fancy_grid',
            'pipe',
            'orgtbl',
            'presto',
            'pretty',
            'psql',
            'rst',
        ]
    )
    return parser


def get_steam_api_key(arg_key: str) -> str:
    if arg_key:
        return arg_key
    env_key = os.environ.get('STEAM_API_KEY')
    if env_key:
        return env_key
    print(
        'Steam API key not found. '
        'Please specify Steam API key as an environment variable (STEAM_API_KEY) '
        'or as a CLI argument (--steam-api-key).'
    )
    sys.exit()


def clear_screen():
    os.system('cls' if os.name =='nt' else 'clear')


def check_server(ip_port: IPPort, stream_api_key: str, table_format: str):
    url = (
        rf'https://api.steampowered.com/IGameServersService/GetServerList/v1/?'
        rf'filter=\gamedir\dayz\gameaddr\{ip_port}&key={stream_api_key}'
    )
    while True:
        resp = requests.get(url)
        if resp.status_code == 200:
            if resp.json()['response']:
                servers = resp.json()['response']['servers']
                table = [{key:server[key] for key in SERVER_KEYS } for server in servers]
                clear_screen()
                print(tabulate(table, headers='keys', tablefmt=table_format))
                time.sleep(10)
            else:
                clear_screen()
                print(f'No servers found!')
                sys.exit()
        else:
            clear_screen()
            print(
                f'Unexpected response from Steam API...\n'
                f'Status code: {resp.status_code}\n'
                f'Response: {resp.text}'
            )
            sys.exit()


def main():
    parser = create_parser()
    args = parser.parse_args()
    steam_api_key = get_steam_api_key(args.steam_api_key)
    try:
        check_server(args.ip_port, steam_api_key, args.table_format)
    except KeyboardInterrupt:
        sys.exit()


if __name__ == '__main__':
    main()
