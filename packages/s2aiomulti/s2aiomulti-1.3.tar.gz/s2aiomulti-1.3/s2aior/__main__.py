#!/usr/bin/env python3
"""
Created on December 16 11:39:15 2015

@author: Alan Yorinks
Copyright (c) 2015 Alan Yorinks All right reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import asyncio
import configparser
import os
import signal
import subprocess
import sys

import aiohttp
from aiohttp import web
import argparse


# noinspection PyMethodMayBeStatic,PyShadowingNames
class S2AIOR:
    """
    This is the "constructor" for the s2aio router.
    It reads the configuration file and sets several class variables
    """

    def __init__(self, config_path):
        path = sys.path

        self.base_path = None

        # get the prefix
        prefix = sys.prefix
        for p in path:
            # make sure the prefix is in the path to avoid false positives
            if prefix in p:
                # look for the configuration directory
                s_path = p + '/s2aior/configuration'
                if os.path.isdir(s_path):
                    # found it, set the base path
                    self.base_path = p + '/s2aior'

        if not self.base_path:
            print('Cannot locate s2aio configuration directory.')
            sys.exit(0)

        print('\nScratch Project Files Located at:')
        print(self.base_path + '/scratch_files/projects\n')

        # grab the config file and get it ready for parsing
        config = configparser.ConfigParser()
        config_file_path = str(self.base_path + '/configuration/configuration.cfg')
        config.read(config_file_path, encoding="utf8")

        # parse the file and place the translation information into the appropriate variable
        self.ln_languages = config.get('translation_lists', 'ln_languages').split(',')
        self.ln_ENABLE = config.get('translation_lists', 'ln_ENABLE').split(',')
        self.ln_DISABLE = config.get('translation_lists', 'ln_DISABLE').split(',')
        self.ln_INPUT = config.get('translation_lists', 'ln_INPUT').split(',')
        self.ln_OUTPUT = config.get('translation_lists', 'ln_OUTPUT').split(',')
        self.ln_PWM = config.get('translation_lists', 'ln_PWM').split(',')
        self.ln_SERVO = config.get('translation_lists', 'ln_SERVO').split(',')
        self.ln_TONE = config.get('translation_lists', 'ln_TONE').split(',')
        self.ln_SONAR = config.get('translation_lists', 'ln_SONAR').split(',')
        self.ln_OFF = config.get('translation_lists', 'ln_OFF').split(',')
        self.ln_ON = config.get('translation_lists', 'ln_ON').split(',')

        # build the arduino routing map
        self.route_map = []
        self.connections = []

        self.poll_reply = ""

        if not config_path:
            hpath = os.path.expanduser('~')
        else:
            hpath = config_path
        self.boards_path = hpath + '/s2aior_boards'
        if not os.path.exists(self.boards_path):
            print('No Arduino Configuration Files Found - run s2aiobe')
            sys.exit(0)

        self.config_file = self.boards_path + '/boards.cfg'

        if not os.path.isfile(self.config_file):
            print('No Arduino Configuration Files Found - run s2aiobe')
            sys.exit(0)

        config.read(self.config_file, encoding="utf8")

        # board numbers range from 1 to 10
        for board_number in range(1, 11):
            # create the section name
            board_string = 'board' + str(board_number)
            # create a dictionary for this section
            items = dict(config.items(board_string))
            # add it to the route map
            self.route_map.append(items)

        loop = asyncio.get_event_loop()
        self.client = aiohttp.ClientSession(loop=loop)

    # noinspection PyShadowingNames
    async def init(self, loop):
        """
        This method initializes the aiohttp server.
        It also instantiate all of the s2aio servers specified in the configuration file.
        After the servers are initialized, the "poll" command is added to the aiohttp server, so that the
        "green" Scratch connectivity indicator stays red until after the servers are instantiated.
        :param loop: asyncio event loop
        :return: http server instance
        """
        app = web.Application(loop=loop)

        app.router.add_route('GET', '/digital_pin_mode/{board}/{enable}/{pin}/{mode}', self.setup_digital_pin)
        app.router.add_route('GET', '/analog_pin_mode/{board}/{enable}/{pin}', self.setup_analog_pin)
        app.router.add_route('GET', '/digital_write/{board}/{pin}/{value}', self.digital_write)
        app.router.add_route('GET', '/analog_write/{board}/{pin}/{value}', self.analog_write)
        app.router.add_route('Get', '/analog_read/{board}/{pin}/{value}', self.got_analog_report)
        app.router.add_route('Get', '/digital_read/{board}/{pin}/{value}', self.got_digital_report)
        app.router.add_route('GET', '/play_tone/{board}/{pin}/{frequency}/{duration}', self.play_tone)

        app.router.add_route('Get', '/problem/{board}/{problem}', self.got_problem_report)
        app.router.add_route('GET', '/set_servo_position/{board}/{pin}/{position}', self.set_servo_position)
        app.router.add_route('GET', '/tone_off/{board}/{pin}', self.tone_off)

        srv = await loop.create_server(app.make_handler(), '127.0.0.1', 50208)

        # instantiate all of the arduino servers
        for x in self.route_map:
            if x['active'] == 'yes':
                #         # usb connected device
                board_id = x['board_id']
                com_port = x['com_port']
                server_address = x['http_server_address']
                server_port = x['http_server_port']
                arduino_ip_address = x['arduino_ip_address']
                arduino_ip_port = x['arduino_ip_port']
                router_ip_address = x['router_address']
                router_ip_port = x['router_port']
                if com_port != 'None':
                    new_s2aios = ['s2aios', '-p', com_port, '-sa', server_address, '-sp', server_port, '-b', board_id,
                                  '-ra', router_ip_address, '-rp', router_ip_port]
                else:
                    new_s2aios = ['s2aios', '-aa', arduino_ip_address, '-ap', arduino_ip_port, '-sa',
                                  server_address, '-sp', server_port, '-b', board_id,
                                  '-ra', router_ip_address, '-rp', router_ip_port]

                print('starting: ' + str(new_s2aios))
                x = subprocess.Popen(new_s2aios)
                self.connections.append(x)
                await asyncio.sleep(2)
        print("Arduino Servers Configured")
        app.router.add_route('GET', '/poll', self.poll)
        await self.keep_alive()

        return srv

    async def setup_digital_pin(self, request):
        """
        This method handles the "set digital pin mode" block request
        :param request: HTTP request
        :return: HTTP response
        """
        command = "digital_pin_mode"
        board = request.match_info.get('board')
        enable = request.match_info.get('enable')
        pin = request.match_info.get('pin')
        mode = request.match_info.get('mode')
        command_string = command + '/' + enable + '/' + pin + "/" + mode
        await self.route_command(board, command_string)
        return web.Response(body="ok".encode('utf-8'))

    async def setup_analog_pin(self, request):
        """
        This method handles the "set analog input pin mode"
        :param request: HTTP request
        :return: HTTP response
        """
        command = "analog_pin_mode"
        board = request.match_info.get('board')
        enable = request.match_info.get('enable')
        pin = request.match_info.get('pin')
        command_string = command + '/' + enable + '/' + pin
        await self.route_command(board, command_string)
        return web.Response(body="ok".encode('utf-8'))

    async def digital_write(self, request):
        """
        This method handles the digital write request
        :param request: HTTP request
        :return: HTTP response
        """
        command = "digital_write"
        board = request.match_info.get('board')
        pin = request.match_info.get('pin')
        value = request.match_info.get('value')
        command_string = command + '/' + pin + '/' + value
        await self.route_command(board, command_string)
        return web.Response(body="ok".encode('utf-8'))

    async def analog_write(self, request):
        """
        This method handles the analog (PWM) write request
        :param request: HTTP request
        :return: HTTP response
        """
        command = "analog_write"
        board = request.match_info.get('board')
        pin = request.match_info.get('pin')
        value = request.match_info.get('value')
        command_string = command + '/' + pin + '/' + value
        await self.route_command(board, command_string)
        return web.Response(body="ok".encode('utf-8'))

    async def play_tone(self, request):
        """
        This method handles the play tone request.
        :param request: HTTP request
        :return: HTTP response
        """
        command = 'play_tone'
        board = request.match_info.get('board')
        pin = request.match_info.get('pin')
        freq = request.match_info.get('frequency')
        duration = request.match_info.get('duration')
        command_string = command + '/' + pin + '/' + freq + '/' + duration
        await self.route_command(board, command_string)
        return web.Response(body="ok".encode('utf-8'))

    async def tone_off(self, request):
        """
        This method turns tone off.
        :param request: HTTP request
        :return: HTTP response
        """
        command = 'tone_off'
        board = request.match_info.get('board')
        pin = request.match_info.get('pin')

        command_string = command + '/' + pin
        await self.route_command(board, command_string)
        return web.Response(body="ok".encode('utf-8'))

    async def set_servo_position(self, request):
        """
        This method sets a servo position.
        :param request: HTTP request
        :return: HTTP response
        """
        command = 'set_servo_position'
        board = request.match_info.get('board')
        pin = request.match_info.get('pin')
        position = request.match_info.get('position')

        command_string = command + '/' + pin + '/' + position
        await self.route_command(board, command_string)
        return web.Response(body="ok".encode('utf-8'))

    # noinspection PyUnusedLocal
    async def poll(self, request):
        """
        This method handles the Scratch poll request for reporter data
        :param request: HTTP request
        :return: HTTP response
        """
        # save the reply to a temporary variable
        total_reply = self.poll_reply

        # clear the poll reply string for the next reply set
        self.poll_reply = ""
        return web.Response(headers={"Access-Control-Allow-Origin": "*"},
                            content_type="text/html", charset="ISO-8859-1", text=total_reply)

    async def got_analog_report(self, request):
        """
        This method handles analog data reports being sent from s2aio servers
        :param request: HTTP request
        :return: HTTP response
        """
        board = request.match_info.get('board')
        pin = request.match_info.get('pin')
        value = request.match_info.get('value')
        self.poll_reply += 'analog_read/' + board + '/' + pin + ' ' + value + '\n'
        # print(request)        # print('aa')
        return web.Response(body="ok".encode('utf-8'))

    async def got_digital_report(self, request):
        """
        This method handles data data reports being sent from s2aio servers
        :param request: HTTP request
        :return: HTTP response
        """
        board = request.match_info.get('board')
        pin = request.match_info.get('pin')
        value = request.match_info.get('value')
        self.poll_reply += 'digital_read/' + board + '/' + pin + ' ' + value + '\n'
        # print(request)        # print('aa')
        return web.Response(body="ok".encode('utf-8'))

    async def got_problem_report(self, request):
        """
        This method handles problem (debugging) reports being sent from s2aio servers
        :param request: HTTP request
        :return: HTTP response
        """
        board = request.match_info.get('board')
        problem = request.match_info.get('problem')
        self.poll_reply += 'problem/' + board + ' ' + problem + '\n'
        return web.Response(body="ok".encode('utf-8'))

    async def route_command(self, board, command):
        """
        This method routes a command coming from Scratch to the appropriate s2aio server
        :param board: index into route map
        :param command: the command string
        :return: HTTP response
        """
        # get http server address and port for the board
        route = self.route_map[int(board) - 1]
        server_addr = route['http_server_address']
        server_port = route['http_server_port']

        url = "http://" + server_addr + ":" + server_port + '/' + command
        async with self.client.get(url) as response:
            return await response.read()

    async def keep_alive(self):
        """
        This method is used to keep the server up and running when not connected to Scratch
        :return:
        """
        while True:
            await asyncio.sleep(1)


def main():
    # noinspection PyShadowingNames

    loop = asyncio.get_event_loop()
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", dest="config_path", default="None",
                        help="Explicitly set the board configuration file location")
    args = parser.parse_args()

    if args.config_path == 'None':
        config_path = None
    else:
        config_path = args.config_path

    s2aior = S2AIOR(config_path)

    # noinspection PyBroadException
    try:
        loop.run_until_complete(s2aior.init(loop))
    except:
        # noinspection PyShadowingNames
        loop = asyncio.get_event_loop()

        sys.exit(0)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print("Control-C detected. See you soon.")
        s2aior.client.close()

        for x in s2aior.connections:
            x.kill()

        for t in asyncio.Task.all_tasks(loop):
            # noinspection PyBroadException
            try:
                t.cancel()
                loop.run_until_complete(asyncio.sleep(.1))
                loop.stop()
                loop.close()
            except:
                pass

        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

    loop = asyncio.get_event_loop()

    # noinspection PyBroadException
    try:
        loop.run_forever()
        loop.stop()
        loop.close()
    except:
        pass
