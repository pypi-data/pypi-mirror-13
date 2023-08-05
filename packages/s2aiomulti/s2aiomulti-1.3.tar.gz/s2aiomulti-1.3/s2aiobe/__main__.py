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

import os
import configparser
import shutil
import argparse

from tkinter import messagebox
from tkinter import *
from tkinter import ttk


class BoardEditor:
    fieldnames = ('Board Number', 'Board Active', 'Arduino COM Port', 'Arduino IP Address', 'Arduino IP Port')
    board_numbers = '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
    active_selectors = 'no', 'yes'

    def __init__(self, config_path):

        self.route_map = []

        # now path was specified
        if not config_path:
            hpath = os.path.expanduser('~')
        else:
            hpath = config_path
        self.boards_path = hpath + '/s2aior_boards'
        if not os.path.exists(self.boards_path):
            os.makedirs(self.boards_path)

        self.config_file = self.boards_path + '/boards.cfg'

        if not os.path.isfile(self.config_file):
            file = open(self.config_file, 'w+')
            for x in range(1, 11):
                board = 'board' + str(x)
                file.write('[' + board + ']\n')
                file.write('board_id = ' + str(x) + '\n')
                file.write('active = no\n')
                file.write('com_port = None\n')
                file.write('http_server_address = 127.0.0.1\n')
                file.write('http_server_port = ' + str(50214 + x) + '\n')
                file.write('arduino_ip_address = None\n')
                file.write('arduino_ip_port = None\n')
                file.write('router_address = 127.0.0.1\n')
                file.write('router_port = 50208\n\n\n')

            file.close()

        # grab the config file and get it ready for parsing
        self.config = configparser.ConfigParser()
        # config_file_path = self.config_file
        self.config.read(self.config_file, encoding="utf8")

        for board_number in range(1, 11):
            # create the section name
            board_string = 'board' + str(board_number)
            # create a dictionary for this section
            items = dict(self.config.items(board_string))
            # add it to the route map
            self.route_map.append(items)

        first_board_data = self.route_map[0]

        self.window = Tk()

        self.window.geometry("400x250+50+50")

        pad_frame = ttk.Frame(self.window, height=20)

        the_frame = ttk.Frame(self.window)

        path = sys.path

        # get the prefix
        prefix = sys.prefix
        for p in path:
            # make sure the prefix is in the path to avoid false positives
            if prefix in p:
                # look for the configuration directory
                s_path = p + '/s2aior/configuration'
                if os.path.isdir(s_path):
                    # found it, set the base path
                    self.base_path = s_path


        # create main window with icon
        self.window.iconphoto(self.window, PhotoImage(file=os.path.join(self.base_path, "logo.png")))
        self.window.title("s2aiobe Board Configuration Editor")

        # create all the labels
        for (ix, label) in enumerate(self.fieldnames):
            ttk.Label(the_frame, text=label).grid(row=ix, sticky=W, padx=10, ipadx=4, ipady=4)

        # create the controls
        # create the board selector combobox
        self.board_selection = ttk.Combobox(the_frame, values=self.board_numbers, state='readonly')
        self.board_selection.current(0)
        self.board_selection.grid(row=0, column=1)
        self.board_selection.bind("<<ComboboxSelected>>", self.board_selected)

        # create the activity selector
        self.active_selection = ttk.Combobox(the_frame, values=self.active_selectors, state='readonly')
        self.active_selection.current(0)
        self.active_selection.grid(row=1, column=1)
        self.active_selection.set(first_board_data['active'])

        # create the COM port entry field
        self.com_port = Entry(the_frame)
        self.com_port.insert(INSERT, first_board_data['com_port'])
        self.com_port.grid(row=2, column=1, ipadx=8, sticky=W)

        # create the IP address entry field
        self.ip_address = Entry(the_frame)
        self.ip_address.insert(INSERT, first_board_data['arduino_ip_address'])
        self.ip_address.grid(row=3, column=1, ipadx=8, sticky=W)

        # create the IP port entry field
        self.ip_port = Entry(the_frame)
        self.ip_port.insert(INSERT, first_board_data['arduino_ip_port'])
        self.ip_port.grid(row=4, column=1, ipadx=8, sticky=W)

        update_board_button = Button(the_frame, text='Update Board Information', command=self.update_board_changes)
        update_board_button.grid(row=6, column=0, pady=30)

        done_button = Button(the_frame, text='Save All Changes', command=self.done)
        done_button.grid(row=6, column=1, pady=30)

        pad_frame.pack()
        the_frame.pack()

    # noinspection PyUnusedLocal
    def board_selected(self, event):
        board = int(self.board_selection.get())
        board -= 1
        board_data = self.route_map[board]
        self.active_selection.set(board_data['active'])

        l = len(self.com_port.get())
        self.com_port.delete(0, l)
        self.com_port.insert(0, board_data['com_port'])

        l = len(self.ip_address.get())
        self.ip_address.delete(0, l)
        self.ip_address.insert(0, board_data['arduino_ip_address'])

        l = len(self.ip_port.get())
        self.ip_port.delete(0, l)
        self.ip_port.insert(0, board_data['arduino_ip_port'])

    def update_board_changes(self):
        data = [self.board_selection.get(), self.active_selection.get(), self.com_port.get(), self.ip_address.get(),
                self.ip_port.get()]
        if data[2] != 'None' and (data[3] != 'None' or data[4] != 'None'):
            messagebox.showerror('Entry Error', 'Cannot Have Both USB Port and IP Information')

        # update the route map for the board
        map_entry = self.route_map[int(data[0]) - 1]
        map_entry['active'] = data[1]
        map_entry['com_port'] = data[2]
        map_entry['arduino_ip_address'] = data[3]
        map_entry['arduino_ip_port'] = data[4]

    def done(self):
        # get a time stamp for the backup file name

        # create a backup file

        backup = self.boards_path + '/backup.cfg'
        shutil.copyfile(self.config_file, backup)

        # now update the config file with the new data
        for i, data in enumerate(self.route_map):
            board = 'board' + str(i + 1)
            self.config.set(board, 'active', data['active'])
            self.config.set(board, 'com_port', data['com_port'])
            self.config.set(board, 'arduino_ip_address', data['arduino_ip_address'])
            self.config.set(board, 'arduino_ip_port', data['arduino_ip_port'])

        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

        sys.exit(0)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", dest="config_path", default="None",
                        help="Explicitly set the board configuration file location")
    args = parser.parse_args()

    if args.config_path == 'None':
        config_path = None
    else:
        config_path = args.config_path

    board_editor = BoardEditor(config_path)
    board_editor.window.mainloop()


if __name__ == "__main__":
    main()
