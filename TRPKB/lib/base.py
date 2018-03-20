#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROGRAM : base
# AUTHOR  : codeunsolved@gmail.com
# CREATED : May 19 2017
# VERSION : v0.0.1

import logging
import os
import re
import shlex
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def get_file_path(dir_main, suffix=None, output_type='list', r_num=2, debug=True):
    def recurse_dir(dir_r, path_list, suffix_r, r_num_r):
        r_num_r -= 1
        content_list = os.listdir(dir_r)
        for content in content_list:
            path_content = os.path.join(dir_r, content)
            if os.path.isdir(path_content) and r_num_r:
                recurse_dir(path_content, path_list, suffix, r_num_r)
            elif re.search('\.{}$'.format(suffix_r), content):
                if debug:
                    print(path_content)
                path_list.append(path_content)
        return path_list

    path_file = recurse_dir(dir_main, [], suffix, r_num)
    if output_type == 'list':
        return path_file
    elif output_type == 'txt':
        return '\n'.join(path_file)


def color_term(string, color='blue'):
    colors = {
        'grey': '\033[1;30m',
        'red': '\033[1;31m',
        'green': '\033[1;32m',
        'yellow': '\033[1;33m',
        'blue': '\033[1;34m',
        'megenta': '\033[1;35m',
        'cyan': '\033[1;36m',
        'white': '\033[1;37m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    return colors[color] + string + colors['end']


class FileHandlerFormatter(logging.Formatter):
    def format(self, record):
        msg = super(FileHandlerFormatter, self).format(record)
        return re.sub('\\033\[[0-8;]+m', '', msg)


class SetupLogger(object):
    def __init__(self, log_name, path_log=None, level=logging.INFO, on_file=True, on_stream=True, log_mode='a',
                 format_fh='%(asctime)s | %(filename)s - line:%(lineno)-4d | %(levelname)s | %(message)s',
                 format_sh='[%(levelname)s] %(message)s',
                 format_date='[%b-%d-%Y] %H:%M:%S'):
        self.log_name = log_name
        self.path_log = path_log
        self.level = level
        self.on_file = on_file
        self.on_stream = on_stream
        self.log_mode = log_mode
        self.format_fh = format_fh
        self.format_sh = format_sh
        self.format_date = format_date
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(level)
        self.add_filehandler()
        self.add_streamhandler()

    def add_filehandler(self):
        if self.on_file:
            if self.path_log:  # handle log directory
                dir_name = os.path.dirname(self.path_log)
                if not os.path.exists(dir_name):
                    print(color_term("[WARNING] directory of log doesn't exist, create it!", 'yellow'))
                    os.makedirs(dir_name)

            file_handler = logging.FileHandler(self.path_log, mode=self.log_mode)
            file_handler.setFormatter(FileHandlerFormatter(self.format_fh, self.format_date))
            self.logger.addHandler(file_handler)

    def add_streamhandler(self):
        if self.on_stream:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(self.format_sh))
            self.logger.addHandler(stream_handler)


def execute_cmd(c):
    p = subprocess.Popen(shlex.split(c), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for line in iter(p.stdout.readline, b''):
        print(line.rstrip())

    error = p.stderr.read().decode()
    if error:
        raise Exception(error)
