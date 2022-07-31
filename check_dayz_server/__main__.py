"""
CLI entrypoint
"""
import argparse
import ipaddress
import os
import sys
import time

import a2s
import requests
from tabulate import tabulate


class IPPort:
    """Class for IP:port object."""

    def __init__(self, value: str):
        """Initiate object and validate values."""
        self.value = value
        self.ip = format(ipaddress.ip_address(value.split(':')[0]))
        self.port = int(value.split(':')[1])
    
    def __str__(self):
        """Return IP:port string."""
        return self.value

    def ip(self):
        """Return IP string."""
        return self.ip

    def port(self):
        """Return port integer."""
        return self.port


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'ip_port',
        metavar='IP:PORT',
        type=IPPort,
        help='Example: 85.190.157.113:10200')
    parser.add_argument(
        '--interval',
        metavar='SECONDS',
        type=int,
        default=10,
        help='Time interval to check the server.'
    )
    parser.add_argument(
        '--show-player-duration',
        dest='show_duration',
        action='store_true',
        help='Show duration each player has been on the server.'
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


def clear_screen():
    """Clear screen."""
    os.system('cls' if os.name =='nt' else 'clear')


def exit_message(message: str):
    """Print message and then wait before exiting."""
    clear_screen()
    print(message)
    time.sleep(10)
    sys.exit()


def get_server_query_port(ip_port: IPPort) -> int:
    """Get server query port."""
    url = f'http://api.steampowered.com/ISteamApps/GetServersAtAddress/v1?addr={ip_port.ip}'
    resp = requests.get(url)
    if resp.status_code == 200:
        servers = resp.json()['response']['servers']
        if servers:
            for svr in servers:
                if svr['gameport'] == ip_port.port:
                    return int(svr['addr'].split(':')[1])
        exit_message(f'Server not found: {ip_port}')
    else:
        exit_message(
            f'Unexpected response from Steam API:\n'
            f'\t{resp.status_code = }\n'
            f'\t{resp.text = }'
        )


def create_server_table(resp) -> list:
    """Create server table."""
    return [{
        'Server Name': resp.server_name,
        'Player Count': f'{resp.player_count}/{resp.max_players}',
        'Ping': f'{int(resp.ping * 1000)}ms'
    }]


def create_player_table(resp: list) -> list:
    """Create player table."""
    player_table = []
    for idx, player in enumerate(resp):
        mins, secs = divmod(int(player.duration), 60)
        hrs, mins = divmod(mins, 60)
        duration = (
            f'{str(hrs) + "h " if hrs else ""}'
            f'{str(mins) + "m " if mins else ""}'
            f'{secs}s'
        )
        player_table.append({
            'Player': idx + 1,
            'Duration': duration
        })
    return player_table


def query_server(ip_port: IPPort, query_port: int, show_duration: bool, interval: int, table_format: str):
    """Query server."""
    query_addr = (ip_port.ip, query_port)
    while True:
        try:
            tables = []
            resp = a2s.info(query_addr)
            table = create_server_table(resp)
            tables.append(table)
            if show_duration is True:
                resp = a2s.players(query_addr)
                table = create_player_table(resp)
                tables.append(table)
            clear_screen()
            for table in tables:
                print(tabulate(table, headers="keys", tablefmt=table_format))
                print()
            time.sleep(interval)
        except TimeoutError:
            print(
                f'Query to server timed out. Is the server restarting?\n'
                f'Trying again in one minute...'
            )
            time.sleep(60)


def main():
    parser = create_parser()
    args = parser.parse_args()
    try:
        query_port = get_server_query_port(args.ip_port)
        query_server(args.ip_port, query_port, args.show_duration, args.interval, args.table_format)
    except KeyboardInterrupt:
        sys.exit()


if __name__ == '__main__':
    main()
