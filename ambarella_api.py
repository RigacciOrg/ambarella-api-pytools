#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Communicate with a SJCAM SJ8PRO through the TCP JSON API.

"""

import datetime
import json
import logging
import shutil
import socket
import subprocess
import sys
import time

__author__ = "Niccolo Rigacci"
__copyright__ = "Copyright 2021 Niccolo Rigacci <niccolo@rigacci.org>"
__license__ = "GPLv3-or-later"
__email__ = "niccolo@rigacci.org"
__version__ = "0.1.0"

# TCP session parameters.
HOST = '192.168.42.1'
PORT = 7878
SOCKET = None
TOKEN = None

AMBA_START_SESSION = 257               # Get initial session token
AMBA_STOP_SESSION = 258                # Terminate the session
AMBA_GET_SETTING = 1                   # Quali altri "type" oltre camera_mode? Forse camera_clock e tutti i settings?
AMBA_SET_SETTING = 2                   # Set a camera setting (see AMBA_GET_ALL_CURRENT_SETTINGS) or other setting "type"
                                       # like camera_clock, camera_mode, save_low_resolution_clip, stream_out_type, ...
AMBA_GET_ALL_CURRENT_SETTINGS = 3      # Get current camera settings. Notice: some settings appear more than once, but
                                       # setting one will change all of them
AMBA_GET_SPACE = 5                     # Get card space (total and free)
AMBA_NOTIFICATION = 7                  # Notification message
AMBA_GET_SINGLE_SETTING_OPTIONS = 9    # Get the list of values accepted by a setting
AMBA_GET_DEVICEINFO = 11               # Get camera brand, model, firmware and API version, etc.
AMBA_GET_BATTERY_LEVEL = 13            # Get power state and battery charge percent
AMBA_CAMERA_OFF = 12                   # Power off the camera (unofficial name)
AMBA_BOSS_RESETVF = 259                # Start RTSP video streaming. Aliases: sendResetVF, sendForceResetVF
AMBA_STOP_VF = 260                     # Stop the video streaming
AMBA_RECORD_START = 513                # Start recording (timelapse, burst, ...)
AMBA_RECORD_STOP = 514                 # Stop recording
AMBA_GET_RECORD_TIME = 515             # Get current recording length (seconds)
AMBA_GET_CURRENT_MODE_SETTINGS = 2053  # Current mode settings, subset of AMBA_GET_ALL_CURRENT_SETTINGS (unofficial name)


# Socket timing parameters.
SOCKET_TIMEOUT_SEC = 5.0           # Default timeout for socket
JSON_BEGIN_TIMEOUT_SEC = 2.0       # Timeout to receive the begin of a JSON message
JSON_MORE_CHARS_TIMEOUT_SEC = 0.2  # Timeout to receive JSON additional chars
JSON_COMPLETE_TIMEOUT_SEC = 4.0    # Overall timeout for JSON message to be complete
NOTIFY_TIMEOUT = 4.0               # Max wait time for AMBA_NOTIFICATION messages

# Camera most important info to get.
CAMERA_INFO = (
    'brand',
    'model',
    'api_ver',
    'firmwareVersion'
)


def api_error(err_id, msg, is_fatal=False):
    """ Log and print the relevant error message """
    logging.error(msg)
    print_big('Err.\n%s' % (err_id,))
    if is_fatal:
        sys.exit(1)


def print_big(msg):
    """ Print a message in big characters """
    if shutil.which('figlet'):
        cmd = ['figlet', '-f', 'big', '-k', msg.replace('_', ' ')]
        subprocess.run(cmd)
    else:
        print(msg)


def get_item(item, dictionary, var_type=None):
    """ Try to get an item from a dictionary, casting to var_type """
    val = None
    if dictionary is not None and item in dictionary:
        if var_type is not None:
            try:
                val = var_type(dictionary[item])
            except Exception as ex:
                logging.info('Exception casting "%s" to %s in "%s" item' % (dictionary[item], var_type.__name__, item))
        else:
            val = dictionary[item]
    return val


def socket_open():
    """ Open a TCP socket to HOST:PORT and set the SOCKET variable """
    global SOCKET
    try:
        SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCKET.settimeout(SOCKET_TIMEOUT_SEC)
        SOCKET.connect((HOST, PORT))
    except Exception as ex:
        logging.error('Exception in socket.connect(): %s' % (ex,))
        SOCKET = None


def socket_send(msg):
    """ Send msg string to SOCKET, return False on error """
    try:
        SOCKET.sendall(msg.encode('utf-8') + b'\n')
    except Exception as ex:
        logging.error('Exception in socket.sendall(): %s' % (ex,))
        return False
    return True


def socket_rcv_json():
    """ Read JSON strings from the SOCKET and return a list of dictionaries """
    data = b''
    data_len = 0
    wait_more_data = True
    t0 = time.time()
    SOCKET.settimeout(JSON_BEGIN_TIMEOUT_SEC)
    while True:
        time.sleep(0.02)  # Allow chars to accumulate.
        try:
            data += SOCKET.recv(4096)
        except socket.timeout as ex:
            if len(data) == 0:
                logging.error('socket_rcv_json(): Nothing received by socket_rcv_json()')
            break
        except Exception as ex:
            logging.error('Exception in socket_rcv_json(): %s' % (ex,))
            break
        SOCKET.settimeout(JSON_MORE_CHARS_TIMEOUT_SEC)
        if data.endswith(b'}'):
            if wait_more_data:
                data_len = len(data)
                wait_more_data = False
            else:
                new_data_len = len(data)
                if new_data_len != data_len:
                    # Receive buffer increased, wait more.
                    data_len = new_data_len
                    wait_more_data = True
                else:
                    # No more data arrived after the "}".
                    break
        else:
            if time.time() - t0 > JSON_COMPLETE_TIMEOUT_SEC:
                logging.warning('Timeout in socket_rcv_json(). Received data so far: %s' % (data,))
                break
    SOCKET.settimeout(SOCKET_TIMEOUT_SEC)
    logging.debug('Received: "%s"' % (data.decode('utf-8')))
    return json_to_dict(data.decode('utf-8'))


def json_to_dict(data):
    """ Convert concatenated JSON strings into a list of dictionaries """
    data = '[' + data.replace('}{','},{') + ']'
    try:
        messages = json.loads(data)
    except Exception as ex:
        logging.warning('Invalid JSON string: %s' % (data,))
        logging.error('Exception parsing JSON string: %s' % (ex,))
        messages = [{}]
    return messages


def make_msg(msg_id, msg_type=None, param=None):
    """ Return a SJCAM message as a JSON string """
    payload = { 'msg_id': msg_id }
    if TOKEN is not None:
        payload['token'] = TOKEN
    if msg_type is not None:
        payload['type'] = msg_type
    if param is not None:
        payload['param'] = param
    json_string = json.dumps(payload, separators=(',', ':'))
    logging.debug('JSON message to send: %s' % (json_string,))
    return json_string


def find_reply(messages, msg_id, msg_type=None):
    """ Search into messages the specified 'msg_id', 'rval'=0 and eventually the 'type' """
    for m in messages:
        if 'rval' in m and 'msg_id' in m:
            if m['msg_id'] == msg_id and m['rval'] == 0 and msg_type is None:
                # Check only 'msg_id' and 'rval'.
                return m
            elif m['msg_id'] == msg_id and m['rval'] == 0:
                # Check also 'type'.
                if 'type' in m and m['type'] == msg_type:
                    return m
    return None


def find_notify(messages, msg_id):
    """ Search messages with msg_id == AMBA_NOTIFICATION, return its 'type' or None """
    for m in messages:
        if 'msg_id' in m and 'type' in m:
            if m['msg_id'] == AMBA_NOTIFICATION:
                return m['type']
    return None


def reply_and_notify(msg_id, msg_type=None, expected_notify=None):
    """ Wait for a specified reply message and a specified notification """
    # Replay message must contain the specified 'msg_id' and 'rval' = 0,
    # also the 'type' must match if != None. The notification must be the
    # one specified. If None for reply or notify not received.
    reply = None
    notify = None
    t0 = time.time()
    while reply is None or notify != expected_notify:
        msgs = socket_rcv_json()
        if reply is None:
            reply = find_reply(msgs, msg_id=msg_id, msg_type=msg_type)
        if notify != expected_notify:
            notify = find_notify(msgs, msg_id=AMBA_NOTIFICATION)
        if (time.time() - t0) > NOTIFY_TIMEOUT:
            break
    return reply, notify


def get_param(msg_id, msg_type=None, var_type=None):
    """ Send the 'msg_id' message and return 'param' and 'type' from the response """
    # Responses generally contains the value into the 'param' item.
    # Some responses contains also the 'type' item.
    # Eventually the 'param' value is casted to var_type.
    socket_send(make_msg(msg_id, msg_type))
    messages = socket_rcv_json()
    reply = find_reply(messages, msg_id)
    p_param = get_item('param', reply, var_type)
    p_type = get_item('type', reply)
    return p_param, p_type


def set_param(msg_type, param):
    """ Send a AMBA_SET_SETTING nessage and return the response with the same 'type' """
    socket_send(make_msg(AMBA_SET_SETTING, msg_type, param))
    messages = socket_rcv_json()
    return find_reply(messages, AMBA_SET_SETTING, msg_type)


def get_message_reply(msg_id):
    """ Send 'msg_id' message and wait for its generic response """
    socket_send(make_msg(msg_id))
    messages = socket_rcv_json()
    return find_reply(messages, msg_id)


def get_token():
    """ Get the communication TOKEN from the camera, via TCP socket """
    global TOKEN
    TOKEN = 0
    socket_open()
    if SOCKET is None:
        api_error('SOCKET', 'Cannot open TCP socket', is_fatal=True)
    TOKEN = get_param(msg_id=AMBA_START_SESSION, msg_type=None, var_type=int)[0]
    if TOKEN is None:
        api_error('TOKEN', 'Cannot get token from camera', is_fatal=True)


def parse_device_info(message):
    """ Parse the message returned by AMBA_GET_DEVICEINFO """
    # Given the response message (dictionary), returns all the camera
    # info (dictionary). Print a warning for missing keys.
    camera_info = {}
    if message is None:
        api_error('DEV.INFO', 'Error getting device info')
    else:
        for item in CAMERA_INFO:
            camera_info[item] = get_item(item, message)
            if camera_info[item] is None:
                api_error('INFO.NA', 'Missing item "%s" in device info' % (item,))
    return camera_info


def parse_camera_settings(message):
    """ Parse the message returned by AMBA_GET_ALL_CURRENT_SETTINGS """
    # Given the response message (dictionary), returns all the camera
    # settings (dictionary). Print a warning for duplicate keys, etc.
    camera_settings = {}
    if message is None or 'param' not in message:
        api_error('SETTINGS', 'Error getting current settings')
    else:
        try:
            for item in message['param']:
                for key in item:
                    val = item[key]
                    if key in camera_settings:
                        if val != camera_settings[key]:
                            # WARNING: Same key with different value!
                            logging.warning('Same setting "%s" with conflicting value: "%s" != "%s"' % (key, camera_settings[key], val))
                        else:
                            # DEBUG: Some keys exist more than once.
                            logging.debug('Setting "%s" exists more than once' % (key,))
                    else:
                        camera_settings[key] = val
        except Exception as ex:
            api_error('PARSE', 'Exception parsing setting "%s": %s' % (key, str(ex)))
    return camera_settings


def close_session():
    """ Send AMBA_STOP_SESSION message and close the TCP socket """
    reply = get_message_reply(msg_id=AMBA_STOP_SESSION)
    if reply is None:
        A.api_error('SESS', 'Error closing session')
    SOCKET.close()
