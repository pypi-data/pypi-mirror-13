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

import argparse
import asyncio
import signal
import sys
import urllib.request

from aiohttp import web
from pymata_aio.constants import Constants
from pymata_aio.pymata_core import PymataCore


# noinspection PyUnusedLocal,PyMethodMayBeStatic
class S2AIOS:
    def __init__(self, com_port=None, version_request=False, ip_address=None,
                 ip_port=None, server_ip_address="127.0.0.1", server_ip_port=50209,
                 board_id=None, router_ip_address="127.0.0.1", router_ip_port=50208):
        """
        This is the constructor for the s2aio server and is called from s2aior to instantiate the server
        :param com_port: Arduino Com port
        :param version_request: Print version
        :param ip_address: If using wifi, ip address of arduino
        :param ip_port: If using wifi, ip port of arduino
        :param server_ip_address: IP address of this server
        :param server_ip_port: IP port of this server
        :param board_id: Board identifier
        :param router_ip_address: IP address of s2aio router
        :param router_ip_port: IP port of s2aio router
        :return: None
        """

        # establish initial base_path - where s2aios lives
        self.ip_address = ip_address
        self.ip_port = ip_port
        self.server_ip_address = server_ip_address
        self.server_ip__port = server_ip_port
        self.board_id = board_id
        self.router_ip_address = router_ip_address
        self.router_ip_port = router_ip_port

        # get version info if requested
        if version_request:
            print()
            print('s2aios version 1.2 - 21 Dec 2015')
            sys.exit(0)

        # arduino com_port to use
        self.com_port = com_port

        # scratch command
        self.command = None

        # HTTP reply to poll request. It is built as needed
        self.poll_reply = ""

        # lists of digital pin capabilities
        # These lists contain the pins numbers that support the capability
        self.input_capable = []
        self.output_capable = []
        self.analog_capable = []
        self.pwm_capable = []
        self.servo_capable = []
        self.i2c_capable = []

        # this contains the numeric "A" (A0, A1..) channel values supported by the board
        self.analog_channel = []

        # this is the total number of pins supported by the connected arduino
        self.num_digital_pins = 0

        # for Snap - a dictionary of pins with their latest values
        self.digital_data = {}
        self.analog_data = {}

        # save last problem reported for snap!
        self.last_problem = ""

        # pymata-aio instance
        self.board = None

        self.loop = None
        # self.client = None

    async def kick_off(self, my_loop):
        """
        After s2aios is instantiated, this method must be called to start the HTTP server,
        instantiate tye pymata_core interface to the arduino board

        :param my_loop: The asyncio event loop
        :return: A reference to this server
        """
        self.loop = my_loop

        # noinspection PyBroadException
        try:
            # instantiate the arduino interface
            self.board = PymataCore(arduino_wait=5, com_port=self.com_port, ip_address=self.ip_address,
                                    ip_port=self.ip_port)
            await self.board.start_aio()

            # populate the arduino pin capability lists
            await self.get_pin_capabilities()

            # start up the HTTP server
            app = web.Application(loop=my_loop)
            srv = await my_loop.create_server(app.make_handler(), self.server_ip_address, self.server_ip__port)

            # Scratch command handlers
            # multi-board
            app.router.add_route('GET', '/multi_board_connect/{board}/{addr}/{port}', self.multi_board_connect)
            app.router.add_route('GET', '/digital_pin_mode/{board}/{enable}/{pin}/{mode}', self.setup_digital_pin)
            app.router.add_route('GET', '/analog_pin_mode/{board}/{enable}/{pin}', self.setup_analog_pin)
            app.router.add_route('GET', '/digital_write/{board}/{pin}/{value}', self.digital_write)
            app.router.add_route('GET', '/analog_write/{board}/{pin}/{value}', self.analog_write)
            app.router.add_route('GET', '/play_tone/{pin}/{board}/{frequency}/{duration}', self.play_tone)
            app.router.add_route('GET', '/set_servo_position/{board}/{pin}/{position}', self.set_servo_position)
            app.router.add_route('GET', '/tone_off/{board}/{pin}', self.tone_off)

            # Snap requires reporters to be supported
            app.router.add_route('GET', '/digital_read/{board}/{pin}', self.digital_read)
            app.router.add_route('GET', '/analog_read/{board}/{pin}', self.analog_read)

            # single board interface

            app.router.add_route('GET', '/digital_read/{pin}', self.digital_read)
            app.router.add_route('GET', '/analog_read/{pin}', self.analog_read)

            app.router.add_route('GET', '/digital_pin_mode/{enable}/{pin}/{mode}', self.setup_digital_pin)
            app.router.add_route('GET', '/analog_pin_mode/{enable}/{pin}', self.setup_analog_pin)
            app.router.add_route('GET', '/poll', self.poll)
            app.router.add_route('GET', '/digital_write/{pin}/{value}', self.digital_write)
            app.router.add_route('GET', '/analog_write/{pin}/{value}', self.analog_write)
            app.router.add_route('GET', '/play_tone/{pin}/{frequency}/{duration}', self.play_tone)
            app.router.add_route('GET', '/set_servo_position/{pin}/{position}', self.set_servo_position)
            app.router.add_route('GET', '/tone_off/{pin}', self.tone_off)

            # Snap requires reporters to be supported
            app.router.add_route('GET', '/digital_read/{pin}', self.digital_read)
            app.router.add_route('GET', '/analog_read/{pin}', self.analog_read)
            app.router.add_route('GET', '/problem', self.problem)
            await self.board.keep_alive()

            await self.keep_alive()
            # self.client = aiohttp.ClientSession(loop=loop)
            return srv
        except:
            pass

    async def send_report(self, url):
        """
        Send a data report to the s2aio router
        :param url: URL used to send report to router
        :return: None
        """
        x = urllib.request.urlopen(url)
        x.read()

    async def get_pin_capabilities(self):
        """
        This method retrieves the Arduino pin capability and analog map reports.
        For each digital pin mode, a list of valid pins is constructed,
        A total pin count is calculated and in addition,
        a list of valid analog input channels is constructed.
        :return: None
        """
        # get the capability report
        pin_capabilities = await self.board.get_capability_report()

        # initialize the total pin count to o
        pin_count = 0

        pin_data = []

        # Each set of digital pin capabilities is delimited by the value of 127
        # Accumulate all of the capabilities into a list for the current pin
        for x in pin_capabilities:
            if x != 127:
                pin_data.append(x)
                continue
            # Found a delimiter, populate the specific capability lists with this pin.
            # Each capability contains 2 bytes. The first is the capability and the second is the
            # number of bits of data resolution for the pin. The resolution is ignored
            else:
                pin__x_capabilities = pin_data[::2]
                for y in pin__x_capabilities:
                    if y == 0:
                        self.input_capable.append(pin_count)
                    elif y == 1:
                        self.output_capable.append(pin_count)
                    elif y == 2:
                        self.analog_capable.append(pin_count)
                    elif y == 3:
                        self.pwm_capable.append(pin_count)
                    elif y == 4:
                        self.servo_capable.append(pin_count)
                    elif y == 6:
                        self.i2c_capable.append(pin_count)
                    else:
                        print('Unknown Pin Type ' + y)
                # clear the pin_data list for the next pin and bump up the pin count
                pin_data = []
                # add an entry into the digital data dictionary
                self.digital_data[pin_count] = 0

                pin_count += 1
        # Done with digital pin discovery, save the pin count
        self.num_digital_pins = pin_count

        # Get analog channel data and create the analog_channel list
        analog_pins = await self.board.get_analog_map()
        for x in analog_pins:
            if x != 127:
                self.analog_channel.append(x)
                self.analog_data[x] = 0

    async def poll(self, request):
        """
        A poll request was received from Scratch. This method sends the HTTP reply to Scratch.
        The reply is built dynamically for each reporter, including error messages, as data
        is received from the Arduino.
        :param request: The HTTP request
        :return: HTTP reply
        """

        # save the reply to a temporary variable
        total_reply = self.poll_reply

        # clear the poll reply string for the next reply set
        self.poll_reply = ""

        # send the HTTP response
        return web.Response(headers={"Access-Control-Allow-Origin": "*"},
                            content_type="text/html", charset="ISO-8859-1", text=total_reply)

    async def multi_board_connect(self, request):
        await self.set_problem('problem 0\n')

        board = request.match_info['board']
        addr = request.match_info['addr']
        port = request.match_info['port']
        # print(str(request))
        return web.Response(body="ok".encode('utf-8'))

    async def setup_digital_pin(self, request):
        """
        This method processes the Scratch "Digital Pin" Block that establishes the mode for the pin
        :param request: The HTTP request
        :return: HTTP reply
        """

        # clear out any residual problem strings
        await self.set_problem('problem 0\n')

        # get the pin string from the block
        pin = request.match_info['pin']

        # convert pin string to integer.
        try:
            pin = int(pin)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 1-1\n')
            return web.Response(body="ok".encode('utf-8'))

        # validate that the pin is within the pin count range
        # pin numbers start with 0
        if pin >= self.num_digital_pins:
            await self.set_problem('problem 1-2\n')
            return web.Response(body="ok".encode('utf-8'))

        # Is the user enabling or disabling the pin? Get the 'raw' value and
        # translate it.
        enable = request.match_info['enable']

        # retrieve mode from command
        mode = request.match_info['mode']

        if enable == 'Enable':
            # validate the mode for this pin
            if mode == 'Input':
                if pin in self.input_capable:
                    # send the pin mode to the arduino
                    await self.board.set_pin_mode(pin, Constants.INPUT,
                                                  self.digital_input_callback, Constants.CB_TYPE_ASYNCIO)
                else:
                    # this pin does not support input mode
                    await self.set_problem('problem 1-3\n')
            elif mode == 'Output':
                if pin in self.output_capable:
                    # send the pin mode to the arduino
                    await self.board.set_pin_mode(pin, Constants.OUTPUT)
                else:
                    # this pin does not support output mode
                    await self.set_problem('problem 1-4\n')
            elif mode == 'PWM':
                if pin in self.pwm_capable:
                    # send the pin mode to the arduino
                    await self.board.set_pin_mode(pin, Constants.PWM)
                else:
                    # this pin does not support output mode
                    await self.set_problem('problem 1-5\n')
            elif mode == 'Servo':
                if pin in self.servo_capable:
                    # send the pin mode to the arduino
                    await self.board.set_pin_mode(pin, Constants.SERVO)
                else:
                    # this pin does not support output mode
                    await self.set_problem('problem 1-6\n')
            elif mode == 'Tone':
                if pin in self.servo_capable:
                    # send the pin mode to the arduino
                    await self.board.set_pin_mode(pin, Constants.OUTPUT)
                else:
                    # this pin does not support output mode
                    await self.set_problem('problem 1-7\n')
            elif mode == 'SONAR':
                if pin in self.input_capable:
                    # send the pin mode to the arduino
                    await self.board.sonar_config(pin, pin, self.digital_input_callback, Constants.CB_TYPE_ASYNCIO)
                else:
                    # this pin does not support output mode
                    await self.set_problem('problem 1-8\n')
            else:
                await self.set_problem('problem 1-9\n')
        # must be disable
        else:
            pin_state = await self.board.get_pin_state(pin)
            if pin_state[1] != Constants.INPUT:
                await self.set_problem('problem 1-10\n')
            else:
                # disable the pin
                await self.board.disable_digital_reporting(pin)

        return web.Response(body="ok".encode('utf-8'))

    async def setup_analog_pin(self, request):
        """
        This method validates and configures a pin for analog input
        :param request:
        :return:
        """
        await self.set_problem('problem 0\n')

        # get the pin string from the block
        pin = request.match_info['pin']

        # convert pin string to integer.
        try:
            pin = int(pin)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 2-1\n')
            return web.Response(body="ok".encode('utf-8'))

        # validate that pin in the analog channel list
        # pin numbers start with 0
        if pin not in self.analog_channel:
            await self.set_problem('problem 2-2\n')
            return web.Response(body="ok".encode('utf-8'))

        # Is the user enabling or disabling the pin? Get the 'raw' value and
        # translate it.
        enable = request.match_info['enable']

        if enable == 'Enable':
            await self.board.set_pin_mode(pin, Constants.ANALOG, self.analog_input_callback, Constants.CB_TYPE_ASYNCIO)
            return web.Response(body="ok".encode('utf-8'))
        else:
            await self.board.disable_analog_reporting(pin)
            return web.Response(body="ok".encode('utf-8'))

    async def digital_write(self, request):
        """
        This method perform a digital write
        :param request: HTTP request
        :return:
        """
        # clear out any residual problem strings
        await self.set_problem('problem 0\n')

        # get the pin string from the block
        pin = request.match_info['pin']

        try:
            pin = int(pin)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 3-1\n')
            return web.Response(body="ok".encode('utf-8'))

        pin = int(request.match_info['pin'])
        pin_state = await self.board.get_pin_state(pin)
        if len(pin_state) == 1:
            await self.set_problem('problem 3-2\n')
            return web.Response(body="ok".encode('utf-8'))

        if pin_state[1] != Constants.OUTPUT:
            await self.set_problem('problem 3-3\n')
            return web.Response(body="ok".encode('utf-8'))

        value = int(request.match_info['value'])
        await self.board.digital_write(pin, value)
        return web.Response(body="ok".encode('utf-8'))

    async def analog_write(self, request):
        """
        This method performs an analog write (pwm)
        :param request: HTTP request
        :return: HTTP reply
        """
        # clear out any residual problem strings
        await self.set_problem('problem 0\n')
        # get the pin string from the block
        pin = request.match_info['pin']

        try:
            pin = int(pin)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 4-1\n')
            return web.Response(body="ok".encode('utf-8'))

        pin = int(request.match_info['pin'])
        pin_state = await self.board.get_pin_state(pin)
        if len(pin_state) == 1:
            await self.set_problem('problem 4-2\n')
            return web.Response(body="ok".encode('utf-8'))

        if pin_state[1] != Constants.PWM:
            await self.set_problem('problem 4-3\n')
            return web.Response(body="ok".encode('utf-8'))

        value = request.match_info['value']
        try:
            value = int(value)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 4-4\n')
            return web.Response(body="ok".encode('utf-8'))

        # validate range of value
        if 0 <= value <= 255:
            await self.board.analog_write(pin, value)
        else:
            await self.set_problem('problem 4-5\n')
        return web.Response(body="ok".encode('utf-8'))

    async def play_tone(self, request):
        """
        This method will play a tone using the Arduino tone library. It requires FirmataPlus
        :param request:The HTTP request
        :return: HTTP response
        """
        # clear out any residual problem strings
        await self.set_problem('problem 0\n')

        # get the pin string from the block
        pin = request.match_info['pin']

        try:
            pin = int(pin)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 5-1\n')
            return web.Response(body="ok".encode('utf-8'))

        pin_state = await self.board.get_pin_state(pin)
        if len(pin_state) == 1:
            await self.set_problem('problem 5-2\n')
            return web.Response(body="ok".encode('utf-8'))

        if pin_state[1] != Constants.OUTPUT:
            await self.set_problem('problem 5-3\n')
            return web.Response(body="ok".encode('utf-8'))

        frequency = request.match_info['frequency']

        try:
            frequency = int(frequency)
        except ValueError:
            # frequency Must Be Specified as an Integer
            await self.set_problem('problem 5-4\n')
            return web.Response(body="ok".encode('utf-8'))

        duration = request.match_info['duration']

        try:
            duration = int(duration)
        except ValueError:
            # frequency Must Be Specified as an Integer
            await self.set_problem('problem 5-5\n')
            return web.Response(body="ok".encode('utf-8'))

        await self.board.play_tone(pin, Constants.TONE_TONE, frequency, duration)
        return web.Response(body="ok".encode('utf-8'))

    async def tone_off(self, request):
        # clear out any residual problem strings
        await self.set_problem('problem 0\n')

        # get the pin string from the block
        pin = request.match_info['pin']

        try:
            pin = int(pin)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 6-1\n')
            return web.Response(body="ok".encode('utf-8'))

        pin_state = await self.board.get_pin_state(pin)
        if len(pin_state) == 1:
            await self.set_problem('problem 6-2\n')
            return web.Response(body="ok".encode('utf-8'))

        if pin_state[1] != Constants.OUTPUT:
            await self.set_problem('problem 6-3\n')
            return web.Response(body="ok".encode('utf-8'))

        await self.board.play_tone(pin, Constants.TONE_NO_TONE, None, None)
        return web.Response(body="ok".encode('utf-8'))

    async def set_servo_position(self, request):
        """
        This method sets a servo position
        :param request: HTTP request
        :return: HTTP reply
        """
        # clear out any residual problem strings
        await self.set_problem('problem 0\n')

        # get the pin string from the block
        pin = request.match_info['pin']

        try:
            pin = int(pin)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 7-1\n')
            return web.Response(body="ok".encode('utf-8'))

        pin_state = await self.board.get_pin_state(pin)
        if len(pin_state) == 1:
            await self.set_problem('problem 7-2\n')
            return web.Response(body="ok".encode('utf-8'))

        if pin_state[1] != Constants.SERVO:
            await self.set_problem('problem 7-3\n')
            return web.Response(body="ok".encode('utf-8'))

        position = request.match_info['position']

        try:
            position = int(position)
        except ValueError:
            # frequency Must Be Specified as an Integer
            await self.set_problem('problem 7-4\n')
            return web.Response(body="ok".encode('utf-8'))

        if 0 <= position <= 180:
            await self.board.analog_write(pin, position)
        else:
            await self.set_problem('problem 7-5\n')
        return web.Response(body="ok".encode('utf-8'))

    async def digital_input_callback(self, arg):
        """
        This method receives digital data inputs
        :param arg: Index 0 = pin and index 1 = value
        :return: None
        """
        self.poll_reply += self.board_id + '/digital_read/' + str(arg[0]) + ' ' + str(arg[1]) + '\n'
        url = 'http://' + self.router_ip_address + ':' + str(self.router_ip_port) + '/digital_read/' + self.board_id + \
              '/' + str(arg[0]) + '/' + str(arg[1])
        # print(url)
        response = await self.send_report(url)
        self.digital_data[arg[0]] = arg[1]

    async def analog_input_callback(self, arg):
        """
        This method receives digital data inputs
        :param arg: Index 0 = pin and index 1 = value
        :return: None
        """
        self.poll_reply += self.board_id + '/analog_read/' + str(arg[0]) + ' ' + str(arg[1]) + '\n'
        url = 'http://' + self.router_ip_address + ':' + str(self.router_ip_port) + '/analog_read/' + self.board_id + \
              '/' + str(arg[0]) + '/' + str(arg[1])
        # print(url)
        response = await self.send_report(url)
        self.analog_data[arg[0]] = arg[1]

    async def digital_read(self, request):
        """
        This method is only used by a snap client, since it does not poll
        :param request:
        :return: HTTP reply
        """
        # clear out any residual problem strings
        await self.set_problem(self.board_id + '/problem 0\n')

        # get the pin string from the block
        pin = request.match_info['pin']

        try:
            pin = int(pin)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 8-1\n')
            return web.Response(body="ok".encode('utf-8'))

        if not (0 <= pin <= self.num_digital_pins):
            await self.set_problem('problem 8-2\n')
            return web.Response(body="ok".encode('utf-8'))

        pin_state = await self.board.get_pin_state(pin)
        if len(pin_state) == 1:
            await self.set_problem('problem 8-3\n')
            return web.Response(body="ok".encode('utf-8'))

        if pin_state[1] != Constants.OUTPUT:
            await self.set_problem('problem 8-3\n')
            return web.Response(body="ok".encode('utf-8'))

        reply = str(self.digital_data[pin]) + '\n'

        # send the HTTP response
        return web.Response(headers={"Access-Control-Allow-Origin": "*"},
                            content_type="text/html", charset="ISO-8859-1", text=reply)

    async def analog_read(self, request):
        """
        This method performs an analog read for a snap client. It is not used by scratch.
        :param request: HTTP request
        :return: HTTP reply
        """
        # clear out any residual problem strings
        await self.set_problem('problem 0\n')

        # get the pin string from the block
        pin = request.match_info['pin']

        try:
            pin = int(pin)
        except ValueError:
            # Pin Must Be Specified as an Integer
            await self.set_problem('problem 9-1\n')
            return web.Response(body="ok".encode('utf-8'))

        pin = int(request.match_info['pin'])

        # validate that pin in the analog channel list
        # pin numbers start with 0
        if pin not in self.analog_channel:
            await self.set_problem('problem 9-2\n')
            return web.Response(body="ok".encode('utf-8'))

        pin_state = await self.board.get_pin_state(pin)
        if len(pin_state) == 1:
            await self.set_problem('problem 9-3\n')
            return web.Response(body="ok".encode('utf-8'))

        reply = str(self.analog_data[pin]) + '\n'

        # send the HTTP response
        return web.Response(headers={"Access-Control-Allow-Origin": "*"},
                            content_type="text/html", charset="ISO-8859-1", text=reply)

    async def problem(self, request):
        """
        This method returns the last saved problem. It is used only by snap.
        :param request: HTTP request
        :return: HTTP reply
        """
        problem = self.last_problem.split(' ')

        # snap can return an empty problem so we need to compensate
        try:
            return web.Response(headers={"Access-Control-Allow-Origin": "*"},
                                content_type="text/html", charset="ISO-8859-1", text=problem[1])
        except IndexError:
            return web.Response(body="ok".encode('utf-8'))

    # noinspection PyMethodMayBeStatic
    async def keep_alive(self):
        """
        This method is used to keep the server up and running when not connected to Scratch
        :return:
        """
        while True:
            await asyncio.sleep(1)

    async def set_problem(self, problem):
        """
        This method adds the problem to the poll reply and saves it as last_problem for snap!
        :param problem:
        :return:
        """
        prob = problem.split()
        rpt = '/' + prob[0] + '/' + self.board_id + '/' + prob[1]
        # problem ='/problem/' +  self.board_id + ' ' + problem
        # self.last_problem = problem
        # self.poll_reply += self.last_problem
        url = 'http://' + self.router_ip_address + ':' + str(self.router_ip_port) + rpt + '\n'
        response = await self.send_report(url)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", dest="comport", default="None", help="Arduino COM port - e.g. /dev/ttyACMO or COM3")
    parser.add_argument("-aa", dest="ip_addr", default="None", help="Arduino IP Address - for WiFi")
    parser.add_argument("-ap", dest="ip_port", default="2000", help="Arduino IP Port - for WiFi")
    parser.add_argument("-sa", dest="server_ip_addr", default="127.0.0.1", help="HTTP Server IP address")
    parser.add_argument("-sp", dest="server_ip_port", default="50209", help="HTTP Server IP port")
    parser.add_argument("-b", dest="board_id", default="None", help="Board Number - 1-10")
    parser.add_argument("-ra", dest="router_addr", default="127.0.0.1", help="Router IP Address")
    parser.add_argument("-rp", dest="router_port", default="50208", help="Router IP port")

    parser.add_argument("-v", action='store_true', help='Print version')

    args = parser.parse_args()

    if args.comport == 'None':
        comport = None
    else:
        comport = args.comport

    if args.server_ip_addr == 'None':
        u_s_ip_addr = None
    else:
        u_s_ip_addr = args.server_ip_addr

    if args.server_ip_port == 'None':
        u_s_ip_port = None
    else:
        u_s_ip_port = args.server_ip_port

    if args.ip_addr == 'None':
        u_ip_addr = None
    else:
        u_ip_addr = args.ip_addr

    if args.ip_port == 'None':
        u_ip_port = None
    else:
        u_ip_port = args.ip_port

    bd_id = args.board_id

    r_addr = args.router_addr
    r_port = args.router_port

    # noinspection PyUnusedLocal
    version = parser.parse_args('-v'.split())

    s2aios = S2AIOS(com_port=comport, version_request=args.v, ip_address=u_ip_addr,
                    ip_port=u_ip_port, server_ip_address=u_s_ip_addr, server_ip_port=u_s_ip_port,
                    board_id=bd_id, router_ip_address=r_addr, router_ip_port=r_port)

    the_loop = asyncio.get_event_loop()

    # noinspection PyBroadException
    try:
        the_loop.run_until_complete((s2aios.kick_off(the_loop)))
    except:
        print('Terminating server for board ' + s2aios.board_id)
        sys.exit(0)

    # signal handler function called when Control-C occurs
    # noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
    def signal_handler(signal, frame):
        print("Control-C detected. See you soon.")
        for t in asyncio.Task.all_tasks(loop):
            t.cancel()
            the_loop.run_until_complete(asyncio.sleep(.1))
            the_loop.stop()
            the_loop.close()
        sys.exit(0)

    # listen for SIGINT
    signal.signal(signal.SIGINT, signal_handler)


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
