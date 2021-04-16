#!/usr/bin/python3

import psutil
import logging
import subprocess
import argparse
import json
import datetime
import threading
from typing import Optional
import sys, os, time, atexit
from sender import send_message_all_online, send_message_all, send_message_to_user

from fastapi import FastAPI
from multiprocessing import Process
import random

import uvicorn

import time
from db_connect import ChangeLogDBConnector


class PackageProcessor:
    def get_curr_state(self):
        PIPE = subprocess.PIPE
        p = subprocess.Popen("apt list --installed", shell=True, stdin=PIPE, stdout=PIPE,
            stderr=subprocess.STDOUT, close_fds=True)
        out = p.stdout.read()
        info = out.decode().split('\n')

        res = dict()

        for lib in info:
            if "," in lib:
                package = dict()
                ver = ''
                border = lib.index('/')
                for i in range(border, border + len(lib[border:])):
                    if lib[i].isnumeric():
                        ver += lib[i]
                        i += 1
                        while lib[i] != ' ':
                            ver += lib[i]
                            i += 1
                        break

                res[lib[:border]] = ver

        return res

    def get_delta(self, left, right):
        delta = dict()
        for key, val in left.items():
            if key not in right:
                delta[key] = val
        return delta

    def get_changed_versions(self, left, right):
        delta = dict()
        for key, val in left.items():
            if key in right and val != right[key]:
                diff = dict()
                diff['old'] = val
                diff['new'] = right[key]
                delta[key] = diff

        return delta




PIPE = subprocess.PIPE

class AptWrapper:
    def install(self, lib):
        p = subprocess.Popen(f"sudo apt-get install {lib} -y", shell=True, stdin=PIPE, stdout=PIPE,
                stderr=subprocess.STDOUT, close_fds=True)
        self.install_out = p.stdout.read().decode()

    def remove(self, lib):
        p = subprocess.Popen(f"sudo apt-get remove {lib} -y", shell=True, stdin=PIPE, stdout=PIPE,
                stderr=subprocess.STDOUT, close_fds=True)
        self.remove_out = p.stdout.read().decode()

    def update(self):
        p = subprocess.Popen(f"sudo apt-get update && sudo apt-get upgrade -y", shell=True, stdin=PIPE, stdout=PIPE,
                stderr=subprocess.STDOUT, close_fds=True)
        self.update_out = p.stdout.read().decode()


app = FastAPI()

@app.get("/add")
async def add(lib: str, response_model=str):
    print(lib)
    processor = PackageProcessor()
    l = processor.get_curr_state()

    db = ChangeLogDBConnector()
    apt = AptWrapper()

    apt.install(lib)

    r = processor.get_curr_state()
    delta = processor.get_delta(r, l)

    msg = ''
    for lib, ver in delta.items():
        db.insert(libname=lib, version=ver, action='add', ts=int(time.time()))
        msg += lib + ', '

    if len(msg) > 2:
        msg = '\"' + 'Added packages: ' + msg[:len(msg) - 2] + '\"'
        send_message_all(msg)
    if len(delta) > 0:
        return 'Installation completed successfully'
    return 'Installation failed. Connect with admin'


@app.get("/delete")
async def delete(lib: str):
    print(lib)
    processor = PackageProcessor()
    l = processor.get_curr_state()

    db = ChangeLogDBConnector()
    apt = AptWrapper()

    apt.remove(lib)

    r = processor.get_curr_state()
    delta = processor.get_delta(l, r)

    msg = ''
    for lib, ver in delta.items():
        db.insert(libname=lib, version=ver, action='del', ts=int(time.time()))
        msg += lib + ', '

    if len(msg) > 2:
        msg = '\"' + 'Deleted packages: ' + msg[:len(msg) - 2] + '\"'
        send_message_all(msg)

    if len(delta) > 0:
        return 'Deinstallation completed successfully'
    return 'Deinstallation failed. Connect with admin'


@app.get("/update")
async def update():
    processor = PackageProcessor()
    l = processor.get_curr_state()

    db = ChangeLogDBConnector()
    apt = AptWrapper()

    apt.update()

    r = processor.get_curr_state()
    delta = processor.get_changed_versions(r, l)

    msg = ''
    for lib, ver in delta.items():
        msg += lib + " " + ver['old'] + "->" + ver['new'] + ', '
        db.insert(libname=lib, version=ver['old'], upd_version=ver['new'], action='del', ts=int(time.time()))

    if len(msg) > 2:
        msg = '\"' + 'Updated packages: ' + msg[:len(msg) - 2] + '\"'
        send_message_all(msg)

    if len(delta) > 0:
        return 'Update completed successfully'
    return 'Update failed. Connect with admin'


def starter():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except Exception as e:
        sys.stderr.write("fork #1 failed: \n")
        sys.exit(1)

    os.chdir(".")
    os.setsid()
    os.umask(0)

    # делаем второй fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        print('started')
    except Exception as e:
        sys.stderr.write("fork #2 failed: \n")
        sys.exit(1)


    # перенаправление стандартного ввода/вывода
    sys.stdout.flush()
    sys.stderr.flush()


if __name__ == "__main__":
    daemonize()
    uvicorn.run(app, host="0.0.0.0", port=8000)


    #proc.join()
