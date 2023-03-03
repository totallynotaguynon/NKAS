import threading

import socketio
from flask import Flask
from flask_socketio import SocketIO, emit

import glo
from common.enum.enum import Path

from module.base.base import BaseModule
from module.thread.thread import *


class Socket(BaseModule):
    app = Flask(__name__)
    socketio = SocketIO(app)
    config = glo.getNKAS().config

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        glo.set_value('socket', self)

    def emit(self, event, data):
        self.socketio.emit(event, data, namespace=self.config.Socket_NameSpace)

    def emitSingleParameter(self, event, key, value):
        self.socketio.emit(event, {key: value}, namespace=self.config.Socket_NameSpace)

    def run(self):
        self.changeWindow()
        self.socketio.run(self.app, port=self.config.Socket_Port, allow_unsafe_werkzeug=True)

    @staticmethod
    @socketio.on('connect', namespace=config.Socket_NameSpace)
    def connect():
        pass

    @staticmethod
    @socketio.on('disconnect', namespace=config.Socket_NameSpace)
    def disconnect():
        pass

    @staticmethod
    @socketio.on('startScheduler', namespace=config.Socket_NameSpace)
    def startScheduler():
        futures.run(glo.getNKAS().loop)

    @staticmethod
    @socketio.on('stopScheduler', namespace=config.Socket_NameSpace)
    def stopScheduler():
        glo.getNKAS().state = False
        for thread in threading.enumerate():
            if 'NKAS' in thread.name:
                threadManager.stopThread(thread)
                continue

    @staticmethod
    @socketio.on('checkSchedulerState', namespace=config.Socket_NameSpace)
    def checkSchedulerStare():
        glo.getSocket().emitSingleParameter('checkSchedulerState', 'state', glo.getNKAS().state)

    @staticmethod
    @socketio.on('checkAllTaskStates', namespace=config.Socket_NameSpace)
    def getAllTaskStates():
        glo.getSocket().emitSingleParameter('checkAllTaskStates', 'data', Socket.config.Task_Dict)

    @staticmethod
    @socketio.on('updateConfigByKey', namespace=config.Socket_NameSpace)
    def updateConfigByKey(data):
        type = data['type']
        callback = data['callback']
        for index, key in enumerate(data['keys']):
            if type == 'task':
                Socket.config.update(key, data['values'][index], Socket.config.Task_Dict, Path.TASK)
            elif type == 'config':
                Socket.config.update(key, data['values'][index], Socket.config.dict, Path.CONFIG)

        glo.getSocket().emit(callback, None)

    @staticmethod
    @socketio.on('getConfigByKey', namespace=config.Socket_NameSpace)
    def getConfigByKey(data):
        type = data['type']
        callback = data['callback']
        result = []
        for index, key in enumerate(data['keys']):
            if type == 'task':
                result.append({'key': key,
                               'value': Socket.config.get(key, Socket.config.Task_Dict)})
            elif type == 'config':
                result.append({'key': key,
                               'value': Socket.config.get(key, Socket.config.dict)})

        glo.getSocket().emit(callback, {'result': result})

    # Setting-General
    @staticmethod
    @socketio.on('hideWindow', namespace=config.Socket_NameSpace)
    def _hideWindow():
        isHidden = Socket.config.get('Socket.HideWindow', Socket.config.dict)
        if isHidden:
            Socket.hideWindow()
        else:
            Socket.showWindow()

    # Setting-Conversation
    @staticmethod
    @socketio.on('getConfigByKeyInConversation', namespace=config.Socket_NameSpace)
    def getConfigByKeyInConversation(data):
        from _conversation import Nikke_list
        for k in data['keys']:
            # 在所有可选的nikke中过滤出已选的
            if k['key'] == 'Task.Conversation.nikkeList':
                k['Nikke_list'] = Nikke_list
                k['Nikke_list_selected'] = Socket.config.get(k['key'], Socket.config.Task_Dict)

        glo.getSocket().emitSingleParameter('getConfigByKeyInConversation', 'data', data)

    # Setting-Simulator
    @staticmethod
    @socketio.on('changeSerial', namespace=config.Socket_NameSpace)
    def changeSerial():
        del glo.getDevice().u2

    @staticmethod
    @socketio.on('checkVersion', namespace=config.Socket_NameSpace)
    def checkVersion():

        pass

