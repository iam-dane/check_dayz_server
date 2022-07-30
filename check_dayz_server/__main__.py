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


STEAM_API_KEY = os.environ.get('STEAM_API_KEY')

SERVER_KEYS = [
    'name',
    'players',
]


class EnvironmentVariableNotFound(Exception):
    pass


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
        metavar='ip:port',
        type=IPPort,
        help='Example: 85.190.157.113:10200')
    return parser


def check_steam_api_key():
    if not STEAM_API_KEY:
        raise EnvironmentVariableNotFound('STEAM_API_KEY')


def clear_screen():
    os.system('cls' if os.name =='nt' else 'clear')


def check_server(ip_port: IPPort):
    url = (
        rf'https://api.steampowered.com/IGameServersService/GetServerList/v1/?'
        rf'filter=\gamedir\dayz\gameaddr\{ip_port}&key={STEAM_API_KEY}'
    )
    while True:
        resp = requests.get(url)
        if resp.status_code == 200:
            if resp.json()['response']:
                servers = resp.json()['response']['servers']
                table = [{key:server[key] for key in SERVER_KEYS } for server in servers]
                clear_screen()
                print(tabulate(table, headers='keys', tablefmt='fancy_grid'))
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
    check_steam_api_key()
    parser = create_parser()
    args = parser.parse_args()
    try:
        check_server(args.ip_port)
    except KeyboardInterrupt:
        sys.exit()


if __name__ == '__main__':
    main()
