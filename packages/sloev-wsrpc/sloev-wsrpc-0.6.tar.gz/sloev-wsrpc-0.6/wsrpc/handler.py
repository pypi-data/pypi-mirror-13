from tornado.gen import coroutine
from tornado.websocket import WebSocketClosedError, WebSocketHandler
from functools import wraps
import base64
import json
import logging

INSTRUCTIONS = {}

def rpc(func):
    func_name = func.__name__
    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs['FUNC_NAME'] = func_name
        return func(*args, **kwargs)
    tmp_func = wrapper
    tmp_func = coroutine(tmp_func)
    INSTRUCTIONS[func_name] = tmp_func

    return tmp_func

OPEN_INSTRUCTIONS = {}
CLOSE_INSTRUCTIONS = {}

def ws_open(func):
    func_name = func.__name__
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    tmp_func = wrapper
    tmp_func = coroutine(tmp_func)
    OPEN_INSTRUCTIONS[func_name] = tmp_func
    return tmp_func

def ws_close(func):
    func_name = func.__name__
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    tmp_func = wrapper
    CLOSE_INSTRUCTIONS[func_name] = tmp_func
    return tmp_func

class WsRPCHandler(WebSocketHandler):
    error_prefix = "[WSRPC catched] %s"
    @coroutine
    def open(self):
        logging.info("ws opened")
        try:
            for func in OPEN_INSTRUCTIONS.values():
                yield func(self)
        except Exception, e:
            logging.exception(self.error_prefix % e.message)

    def push(self, msg_data, callback_id=None, FUNC_NAME=None):
        if callback_id is None or FUNC_NAME is None:
            raise ValueError("push missing args")
        json_dict = {
                'args':msg_data,
                'callback_id':callback_id,
                'instruction':FUNC_NAME
                }
        string = json.dumps(json_dict)
        try:
            self.write_message(string)
        except WebSocketClosedError, e:
            logging.exception(self.error_prefix % e.message)

    def on_close(self):
        logging.info("ws closed")
        try:
            for func in CLOSE_INSTRUCTIONS.values():
                func(self)
        except Exception, e:
            logging.exception(self.error_prefix % e.message)

    @coroutine
    def on_message(self, string):
        instruction = None
        try:
            if not isinstance(string, basestring):
                raise ValueError("not string")
            json_dict = json.loads(string)
            if not isinstance(json_dict, dict):
                raise ValueError("not dict")
            if not 'args' in json_dict:
                json_dict['args'] = None

            instruction = json_dict['instruction']
            callback_id = json_dict['callback_id']
            args = json_dict['args']

            func = INSTRUCTIONS[instruction]
            yield func(self, args, callback_id)
        except KeyError, e:
            logging.exception(self.error_prefix % e.message)
        except ValueError, e:
            logging.exception(self.error_prefix % e.message)


