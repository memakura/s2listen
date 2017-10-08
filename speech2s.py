#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Speech to Scratch
  2017.6
  Hiroaki Kawashima
  Description:
    Create one client for connecting to Julius
    and one server which accpets scratch requests
"""

import os
import sys
import subprocess
import time
import argparse

import socket
import xml.etree.ElementTree as ET

import urllib
import asyncio
from aiohttp import web

class JuliusClient(asyncio.Protocol):
    """ Client for Julius module mode """
    def __init__(self, loop):
        self.loop = loop  # the event loop
        self.transport = None   # used for sending data
        self.cnt = 0  # for debug
        self.totalcnt = 0  # for debug
        self.__debug = True  # for debug
        self.buf = ""  # data from Julius server
        self.heard_sentence = ""  # recognized sentence (always updated)
        self.recog_request = False
        self.recog_sentence = ""  # recognized sentence (updated only when requested)
        self.recog_word = {} # recognized word with specified class
        self.wclass_list = ["名詞", "動詞", "形容詞", "形容動詞", "代名詞", "感動詞", "助詞", "助動詞"]

        # the maximum appeared word number of each word class in the past
        self.max_recog_word = 10
        self.max_past_recog_word = dict(zip(self.wclass_list,
                                            [self.max_recog_word for i in range(len(self.wclass_list))]))
        print(self.max_past_recog_word)
        self.clear_recog()
        print("=== Initialized JuliusClient ===\n")

    def clear_recog(self):
        """ clear current results """
        self.recog_sentence = ""
        for cls in self.wclass_list:
            self.recog_word[cls] = [] # empty

    def stopstart_recog(self):
        """ terminate and resume julius """
        print("stopstart_recog")
        self.transport.write('TERMINATE\n'.encode())
        self.transport.write('RESUME\n'.encode())

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print("Connection made from {peer}".format(peer=peername))
        self.transport = transport

    def data_received(self, data):
        """ Core function of speech recognition """
        self.buf += data.decode()
        self.cnt += 1
        #if self.__debug: print("[count={0:d}] buf:\n{1}---------".format(self.cnt, self.buf))
        if self.buf[-2:] != ".\n":   # check end two chars are terminal (".\n")
            return # concatenate next received buf
        else:
            self.totalcnt += 1
            #if self.__debug:
            #    print("[total={0:d}] totalbuf:\n{1}---------".format(self.totalcnt, self.buf))
            while self.buf:
                place = self.buf.find(".\n")
                xml_str = self.buf[0:place]
                if len(xml_str) == 0:
                    break
                self.buf = self.buf[place+2:]
                xml_str = xml_str.replace('"<', '"(').replace('>"', ')"')
                if self.__debug:
                    print('x=', xml_str)
                root = ET.fromstring(xml_str)
                if self.__debug:
                    print(root.tag)
                if root.tag == 'RECOGOUT':
                    wc_list = [(i.get('WORD'), i.get('CLASSID')) for i in root.iter()]
                    self.parse_wordclass_list(wc_list)
            self.buf = ""

    def parse_wordclass_list(self, wc_list):
        """ parse word-class list and store the results into recog_sentence, recog_word, etc. """
        # CLASSID = word+class
        wc_list = [tuple(e[1].split('+')) for e in wc_list
                    if e[0] is not None and e[0] != '。' and e[0] != '']
        if self.__debug:
            print("word_class_list: ", wc_list)
        if len(wc_list) > 0:
            self.heard_sentence = ''.join([wc[0] for wc in wc_list])
            if self.recog_request:
                self.recog_sentence = self.heard_sentence
                for cls in self.wclass_list:
                    self.recog_word[cls] = [wc[0] for wc in wc_list if wc[1] == cls]
                    if len(self.recog_word[cls]) > self.max_past_recog_word[cls]:
                        self.max_past_recog_word[cls] = len(self.recog_word[cls])
                self.recog_request = False
            print('recog_sentence: ', self.recog_sentence)

    def connection_lost(self, exc):
        print("Connection lost")
        self.loop.stop()

    def __call__(self):
        """ required for passing an instance of this class to loop.create_connection """
        return self


class S2Julius:
    """ scratch 2 julius """
    def __init__(self, use_dnn=False, julius_env=""):
        self.helper_host = "127.0.0.1"
        self.helper_port = 50211 # port of this helper

        self.julius_host = self.helper_host
        self.julius_port = 10500 # port for connecting to julius
        self.julius_proc = None # Julius subprocess handler
        self.julius_dir = r".\julius"
        self.julius_exe = "julius.exe"
        self.main_jconf = "main.jconf"
        self.gmm_jconf = "am-gmm.jconf" # for GMM model
        self.dnn_jconf = "am-dnn.jconf" # for DNN model
        self.dnnconf = "julius.dnnconf"
        self.use_dnn = use_dnn
        self.julius_cmd = julius_env  # for non-default input device
        self.julius_cmd += "start {0} -module {1} -C {2}".format(
            os.path.join(self.julius_dir, self.julius_exe),
            self.julius_port,
            os.path.join(self.julius_dir, self.main_jconf))
        if self.use_dnn:
            self.julius_cmd += " -C {0} -dnnconf {1}".format(
                os.path.join(self.julius_dir, self.dnn_jconf),
                os.path.join(self.julius_dir, self.dnnconf))
            self.julius_waittime_for_launch = 8
        else:
            self.julius_cmd += " -C {0}".format(
                os.path.join(self.julius_dir, self.gmm_jconf))
            self.julius_waittime_for_launch = 4

        self.bufsize = 4096 # bufsize for communicating with Julius module
        self.max_waittime = 10  # max wait sec for recognition
        self.min_waittime = 1
        self.check_cycle = 0.5 # seconds for one awaytio.sleep cycle

        self.waiting_commands = set() # waiting block in scratch
        self.pollresponse_template = ""
        self.pollresponse_flush = ""

        self.poll_flush_request = False

    def julius_launch(self):
        """ start julius.exe """
#        self.julius_proc = subprocess.run("start cmd /c run-win-module.bat", shell=True)
        self.julius_proc = subprocess.Popen(self.julius_cmd, shell=True)
        time.sleep(self.julius_waittime_for_launch)
         # subprocess.run("start run-win-module.bat", shell=True) # window does not close finally

    def julius_kill(self):
        """ kill julius process """
        self.julius_proc.kill()

    async def recogwait(self, request):
        """ wait until either something is recognized 
            or waittime elapses
        """
        try:
            val = int(request.match_info['waittime'])
        except ValueError:
            print("Ignored. Not a number: ", request.match_info['waittime'])
            return web.Response(text="failed")
        command_id = request.match_info['command_id']
        self.waiting_commands.add(command_id)
        if val > self.max_waittime: self.waittime = self.max_waittime
        elif val < self.min_waittime: self.waittime = self.min_waittime
        else: waittime = val
        print("recogwait: ", waittime)

        # request recognition and wait for waittime
        self.jcl.recog_request = True
        self.jcl.clear_recog()
        self.create_pollresponse_flush()
        elapsedtime = 0
        self.jcl.stopstart_recog() # terminate and resume Julius
        while self.jcl.recog_request and elapsedtime < waittime:
            await asyncio.sleep(self.check_cycle)
            elapsedtime += self.check_cycle
        self.jcl.recog_request = False
        self.waiting_commands.remove(command_id)
        return web.Response(text='ok')

    def create_pollresponse_flush(self):
        """ create a poll response for flushing variables in the scratch """
        text = ""
        text += "recogsentence\n"
        for clsid in range(len(self.jcl.wclass_list)):
            cls = self.jcl.wclass_list[clsid]
            text += "numrecogword/{0} 0".format(cls) + "\n"
            text += "numrecogword_by_clsid/{0} 0".format(clsid+1) + "\n"
            text += "recogword/" + "\nrecogword/".join(
                ["{0}/{1}".format(i+1, cls) for i in range(self.jcl.max_past_recog_word[cls])]
                ) + "\n"
            text += "recogword_by_clsid/" + "\nrecogword_by_clsid/".join(
                ["{0}/{1}".format(i+1, clsid+1) for i in range(self.jcl.max_past_recog_word[cls])]
                ) + "\n"
        self.pollresponse_flush = text
        self.poll_flush_request = True

    def create_pollresponse_flush_all(self):
        """ create a poll response for flushing variables including heardsentence """
        self.create_pollresponse_flush()
        self.pollresponse_flush += "heardsentence\n"

    def create_pollresponse_template(self):
        """ create a template of a poll response text """
        text = ""
        text += "numwclass " + str(len(self.jcl.wclass_list)) + "\n"
        text += "wclassname/" \
            + "\nwclassname/".join(["{0} {1}".format(i+1, self.jcl.wclass_list[i])
                                    for i in range(len(self.jcl.wclass_list))]) \
            + "\n"
        self.pollresponse_template = text

    async def poll(self, request):
        """ response to polling from scratch """
        text = self.pollresponse_template
        if self.poll_flush_request:
            text += self.pollresponse_flush
            self.poll_flush_request = False
        else:
            if len(self.jcl.heard_sentence) > 0:
                text += "heardsentence " + urllib.parse.quote(self.jcl.heard_sentence) + "\n"
            if len(self.jcl.recog_sentence) > 0:
                text += "recogsentence " + urllib.parse.quote(self.jcl.recog_sentence) + "\n"
    #        for cls in self.jcl.wclass_list:
            for clsid in range(len(self.jcl.wclass_list)):
                cls = self.jcl.wclass_list[clsid]
                text += "numrecogword/{0} {1}".format(cls, len(self.jcl.recog_word[cls])) + "\n"
                text += "numrecogword_by_clsid/{0} {1}".format(clsid+1, len(self.jcl.recog_word[cls])) + "\n"
                # Formatting recog_word for each word class (noun, verb, ...)
                if len(self.jcl.recog_word[cls]) > 0:
                    text += "recogword/" \
                        + "\nrecogword/".join(
                            ["{0}/{1} {2}".format(i+1, cls, self.jcl.recog_word[cls][i])
                            for i in range(len(self.jcl.recog_word[cls]))]
                            )  + "\n"
                    # Following codes are for the specification of scratch 2 offline extension
                    # For accessing words by class ID (text cannot be inserted into pulldown menu (%m))
                    text += "recogword_by_clsid/" \
                        + "\nrecogword_by_clsid/".join(
                            ["{0}/{1} {2}".format(i+1, clsid+1, self.jcl.recog_word[cls][i])
                            for i in range(len(self.jcl.recog_word[cls]))]
                            ) + "\n"
        text += "_busy "
        text += " ".join(self.waiting_commands)
        #print(text) # for debug
        return web.Response(text=text)

    async def crossdomain(self, request):
        """ response to crossdomain policy request """
        text = '<cross-domain-policy>'
        text += '<allow-access-from domain="*" to-ports="' + str(self.helper_port) + '"/>'
        text += '</cross-domain-policy>'
        return web.Response(text=text)

    def main(self):
        """ launch server/client """
        self.julius_launch() # start julius.exe (server)

        loop = asyncio.get_event_loop()

        # create julius client
        self.jcl = JuliusClient(loop)
        julius_conn = loop.create_connection(self.jcl, self.julius_host, self.julius_port)
        self.create_pollresponse_flush_all()

        # create server for scratch
        app = web.Application(loop=loop)
        app.router.add_get("/recogwait/{command_id}/{waittime}", self.recogwait)
        app.router.add_get("/poll", self.poll)
        app.router.add_get("/crossdomain.xml", self.crossdomain)
        #web.run_app(app, host=self.helper_host, port=self.helper_port)
        scratch_server = loop.create_server(app.make_handler(), self.helper_host, self.helper_port)

        self.create_pollresponse_template()

        try:
            loop.run_until_complete(asyncio.wait({julius_conn, scratch_server}))
            loop.run_forever() # until loop.stop()
        finally:
            loop.close()
            self.julius_kill()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", dest="amodel", default="GMM", help="default = GMM [GMM | DNN]")
    parser.add_argument("-d", dest="device", default="None",
                        help="default = None [None | (choose device number)]")
    args = parser.parse_args()

    # set acoustic model
    USE_DNN = False
    if args.amodel == 'DNN':
        USE_DNN = True
        print("speech2s: using DNN")
    elif args.amodel == 'GMM':
        USE_DNN = False
        print("speech2s: using GMM")
    else:
        USE_DNN = False # use GMM
        print("speech2s: no such model: ", args.amodel)
        print("use default GMM model")

    # set julius env for non-default audio-input device
    JULIUS_ENV = ""
    if args.device != 'None' and args.device.isdigit():
        if int(args.device) > 0:
            print("set PORTAUDIO_DEV_NUM= " + args.device)
            JULIUS_ENV = "(set PORTAUDIO_DEV_NUM={devnum}) && ".format(devnum=int(args.device))
        else:
            print("ignore device number: " + args.device)

    s2julius = S2Julius(USE_DNN, JULIUS_ENV)
    s2julius.main()
