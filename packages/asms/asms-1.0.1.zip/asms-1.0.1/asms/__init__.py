#!/usr/bin/python3
################################################################################
#
# Copyright (c) 2015-2016 BaseIT, http://baseit.pl
#
# Module:  asms.py 
# Version: 1.0.1
# Build:   2016.01.08 18:23:04
#
# Target:  Python 3.5, 3.4, 3.3, 3.2 
#
# Dependencies:
#   For Python version 3.4 and above uses stdlib with no external dependencies
#                      3.3 and below dependent on module enum34 
#                          (pip install enum34)
# Description:
#   The asms module is designated to provide Python SMS interface, enabling 
#   Python scripts to send text messages (SMSes) via aText mobile application.
# 
# More information and download: 
#   http://baseit.pl/#product-asms
#
# Application aText:
#   - more information: http://baseit.pl/#product-aText
#   - download:         http://baseit.pl/#dload-atext
#
#
# This module may be downloaded, installed, run and used in accordance with 
# the terms of the MIT license:
#
#     Copyright (c) 2015-2016 BaseIT
#     Permission is hereby granted, free of charge, to any person obtaining 
#     a copy of this software and associated documentation files 
#     (the "Software"), to deal in the Software without restriction, including
#     without limitation the rights to use, copy, modify, merge, publish, 
#     distribute, sublicense, and/or sell copies of the Software, and to permit
#     persons to whom the Software is furnished to do so, subject to the
#     following conditions:
# 
#     The above copyright notice and this permission notice shall be included in
#     all copies or substantial portions of the Software.
# 
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#     THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#     DEALINGS IN THE SOFTWARE.
#
################################################################################


__all__ = ['SMS', 'ServerResponse', 'ServerResponseCode',
           'IllegalArgumentError', 'IllegalStateError', 'SecurityException',
           'TooManyServersFound',
           'netmask2ip', 'ip2b', 'b2ip', 'all_network_ip_addresses',
           'get_main_network_interface_id', 'get_main_network_interface',
           'retrieve_own_ip', 'retrieve_own_netmask', 'retrieve_own_gateway',            
           'using_netifaces', 'get_version']


import os
import sys
import platform
import socket
import ssl
import json
import ctypes
import threading
from enum import Enum

_use_netifaces = True
try:
    import netifaces
except ImportError:
    _use_netifaces = False

ENV_PASS_VARIABLE  = "SMSPASS"
ENV_PHONE_VARIABLE = "SMSPHONE"

_SYSTEM_WINDOWS = "Windows"

_DEFAULT_UDP_PORT = 1410
_DEFAULT_TCP_PORT = 1410
_DEFAULT_UDP_WAIT_TIME = 1
_DEFAULT_MAX_SERVER_FINDING_ATTEMPTS = 16
_DATAGRAM_BUFFER_SIZE = 64

AINFO_CONTACT_NAME = "contact-name"
AINFO_SMS_MESSAGE  = "sms-message"
AINFO_SENT_FROM    = "sent-from"
AINFO_SMSC_TIME    = "smsc-time"
AINFO_RECEIVE_TIME = "receive-time"


_MAGIC_QUERY     = b'BRY#QUERY?'
_MAGIC_RESPONSE  = b'BRY#ANS!'
_MAGIC_WRONG     = b'BRY#WRONG!!!'
_MAGIC_ADVERTISE = b'BRY#ADVERTISE#'

_SMS_KEY_MOBILE  = "mobile"
_SMS_KEY_TEXT    = "text"
_PROTOCOL_CP     = "ascii"

_PEM = [
    "-----BEGIN CERTIFICATE-----",
    "MIIC4zCCAcugAwIBAgIEGnySSDANBgkqhkiG9w0BAQsFADAiMSAwHgYDVQQDExdCUlkgT1U9SVQg",
    "Tz1iYXNlaXQgQz1QTDAeFw0xNTA2MjQyMDMyMDhaFw0yNTA2MjEyMDMyMDhaMCIxIDAeBgNVBAMT",
    "F0JSWSBPVT1JVCBPPWJhc2VpdCBDPVBMMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA",
    "xWRLYVrE8gOWy1RZoKeGrDvJd2mdOH/Ohu1l1S8Fg3mtfIRgfFeydLI9lahxpQI4C37jipgr8U1E",
    "XcZkJDK1mq6aoi1j4uAmpLS50Rv504aX9q8gSzrNaknGGptlO745yoVDU52V0BsIXBTJ/ksZF1ja",
    "j1EaA5084pKP+RMJoKXumGsXhwtr+MdPHXh9iRmRsa7G037Ae6xR71kaHYhPHmJHD9zsDPWCEJ6I",
    "kgJhLjouTxugrezGpLmAVR2J7y3CuZm5ccyufi74QepDUEM6AyvGbPlPhQCdxDtU9U6gXfA/+PcP",
    "FyawTJ0sCGjE0kA9FO4MLHQ49Hp3bGu1R9N0KQIDAQABoyEwHzAdBgNVHQ4EFgQUa1cXHglihs7e",
    "SIbvu2z+49U2gHcwDQYJKoZIhvcNAQELBQADggEBAAjZyZtYeV42i/kc2eQO/4fiTKRYjFXWZTUc",
    "fYvD0JnJSqJCawxyb+vYUArTcgTJq32s+NxojL5cjQnrmBN88sRM8kJ5BaP+UJNUk84vjYtZrV0e",
    "FZDWsu+1HDMpYMszhduoHjOLPi6RBOxON6N/pVaMqXToZiFv6OXrgwhLIknsu2NiCv8d9J5pGhar",
    "qXJnW/NAOaINzQNEzMSkzcRw1tgALppyKdnkSWsXcQS7eWGGUK5b1zddU0Ccu8yLX6+FX3vXanWb",
    "XfqIQOCzqaenoEODf5HvBexgR4Ao9obzuYJh59VTXP9+gcT94fi3e839z1mYRe96+LdEYVj6OthV",
    "7XQ=",
    "-----END CERTIFICATE-----"
]

_main_network_interface = None    

class IllegalArgumentError(ValueError):
    pass

class IllegalStateError(ValueError):
    pass
    
class SecurityException(Exception):
    pass

class TooManyServersFound(SecurityException):
    pass

def get_version():
    return "1.0.1"

def get_build_date():
    return "2016.01.08 18:23:04"

def using_netifaces():
    return _use_netifaces

def _get_pem():
    system = platform.system()
    base_name = os.path.splitext(os.path.basename(__file__))[0] + os.extsep + "pem" 
    result = os.path.join(os.path.expanduser("~"), ("" if system == _SYSTEM_WINDOWS else ".") + base_name)

    if not os.path.isfile(result):
        with open(result, 'w') as f:
            for line in _PEM:
                print(line, file = f)
        if system == _SYSTEM_WINDOWS:
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(result, FILE_ATTRIBUTE_HIDDEN)
        else:
            try:
                os.chflags(result, os.stat.UF_HIDDEN)
            except AttributeError:
                pass
    
    return result

def _prot_encode(txt):
    return txt.encode(_PROTOCOL_CP, "ignore")
    
def _prot_decode(b):
    return b.decode(_PROTOCOL_CP, "ignore")
    
def _get_magic_query(phone):
    return _MAGIC_QUERY + _prot_encode(phone)

def _get_magic_query_string(phone, password):
    return _prot_decode(_MAGIC_QUERY) + phone + "#" + password

def _get_magic_response_string(phone):
    return _prot_decode(_MAGIC_RESPONSE) + phone

def _get_magic_response(phone):
    return _MAGIC_RESPONSE + _prot_encode(phone)

def netmask2ip(netmask_bits):
    if netmask_bits < 1 or netmask_bits > 31:
        raise IllegalArgumentError("Invalid number of bits specified as network mask ({})".format(netmask_bits))
    result = 0xFFFFFFFF << (32 - netmask_bits)
    return b2ip(result)

def ip2b(dot_address):
    r = 0
    for x in dot_address.split('.'):
        r = (r << 8 ) | int(x)
    return r
    
def b2ip(bin_address):
    return ".".join((lambda n: str(bin_address >> n & 0xFF))(n) for n in [24,16, 8, 0])

def all_network_ip_addresses(dot_ip, dot_netmask):
    b_netmask = ip2b(dot_netmask)
    b_network = ip2b(dot_ip) & b_netmask
    network_size = b_netmask ^ 0xFFFFFFFF 
    return [(lambda a: b2ip(b_network + a))(n) for n in range(1, network_size)]    

def get_main_network_interface_id():
    result = None
    if _use_netifaces:
        try:
            ip_gateway = netifaces.gateways()["default"][netifaces.AF_INET]
            result = ip_gateway[1]
        except (KeyError, IndexError):
            pass
    return result

def get_main_network_interface():
    global _main_network_interface
    if _use_netifaces and _main_network_interface is None:
        main_network_interface_id = get_main_network_interface_id()
        if not main_network_interface_id is None:
            _main_network_interface = netifaces.ifaddresses(get_main_network_interface_id())[netifaces.AF_INET][0]
    return _main_network_interface

def retrieve_own_ip():
    result = None
    errors = []
    
    if _use_netifaces:
        main_ip_interface = get_main_network_interface()
        if not main_ip_interface is None:
            result = main_ip_interface["addr"]
            
    if result is None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(('8.8.8.8', 0))
                result = s.getsockname()[0]
        except OSError as e:
            errors.append(str(e))

        if result is None:
            try:
                host_name = socket.gethostname()
                for a in socket.getaddrinfo(host_name, None, family=socket.AF_INET, flags=socket.AI_CANONNAME | socket.AI_PASSIVE):
                    h = a[3]
                    if h.startswith(host_name):
                        result = a[4][0]
                        break
            except OSError as e:
                errors.append(str(e))

        if result is None or result.startswith("127."):
            raise IllegalStateError("Cannot retrieve usable own IP address" + (": " + "; ".join(errors)) if len(errors) > 0 else "")
            
    return result

def retrieve_own_netmask():
    result = None
    
    if _use_netifaces:
        main_ip_interface = get_main_network_interface()
        if not main_ip_interface is None:
            result = main_ip_interface["netmask"]
            
    return result
    
def retrieve_own_gateway():
    result = None
    
    if _use_netifaces:
        try:
            result = netifaces.gateways()["default"][netifaces.AF_INET][0]
        except (KeyError, IndexError):
            pass
            
    return result


class ServerResponseCode(Enum):
    confirmed = "OK"
    rejected = "REJECTED"
    error = "ERROR"
    
    @staticmethod
    def create(new_value):
        v = new_value.lower()
        for name, member in ServerResponseCode.__members__.items():
            if v == member.value.lower():
                return member
        raise IllegalArgumentError("value of '{}' cannot be converted to ServerResponseCode enum".format(new_value))

class _ServerCommand(Enum):
    quit = "quit"
    sms = "sms"
    check = "check"

    @staticmethod
    def create(new_value):
        v = new_value.lower()
        for name, member in _ServerCommand.__members__.items():
            if v == member.value.lower():
                return member
        raise IllegalArgumentError("value of '{}' cannot be converted to _ServerCommand enum".format(new_value))
    

class ServerResponse:
    def __init__(self, raw_server_response):
        if raw_server_response is None:
            raise IllegalArgumentError("Invalid (empty) server response")
        if not type(raw_server_response) in [list, tuple]:
            raise IllegalArgumentError("Wrong server response type")
        if len(raw_server_response) == 0:
            raise IllegalArgumentError("Invalid (empty) server response")
        
        self._response_code = raw_server_response[0]
        if len(raw_server_response) > 1:
            self._reponse_text = raw_server_response[1]
        else:
            self._reponse_text = ""
            
        if len(raw_server_response) > 2:
            self._additional_response = raw_server_response[2]
        else:
            self._additional_response = {}
            
        return
    
    def get_code(self):
        return(self._response_code)
    
    def is_confirmed(self):
        return(self._response_code is ServerResponseCode.confirmed)

    def is_rejected(self):
        return(self._response_code is ServerResponseCode.rejected)

    def is_error(self):
        return(self._response_code is ServerResponseCode.error)

    def get_message(self):
        return(self._reponse_text)
        
    def has_info(self, label):
        return(label in self._additional_response)
    def get_info(self, label):
        if self.has_info(label):
            return(self._additional_response[label])
        return(None)
    
    def has_contact_name(self):
        return(self.has_info(AINFO_CONTACT_NAME))
    def get_contact_name(self):
        return(self.get_info(AINFO_CONTACT_NAME))    

    def has_sms_message(self):
        return(self.has_info(AINFO_SMS_MESSAGE))
    def get_sms_message(self):
        return(self.get_info(AINFO_SMS_MESSAGE))    

    def has_sent_from(self):
        return(self.has_info(AINFO_SENT_FROM))
    def get_sent_from(self):
        return(self.get_info(AINFO_SENT_FROM))    

    def has_smsc_time(self):
        return(self.has_info(AINFO_SMSC_TIME))
    def get_smsc_time(self):
        return(self.get_info(AINFO_SMSC_TIME))    

    def has_receive_time(self):
        return(self.has_info(AINFO_RECEIVE_TIME))
    def get_receive_time(self):
        return(self.get_info(AINFO_RECEIVE_TIME))    
        
class SMS:
    
    def __init__(self, phone = None, password = None,
                 own_ip_address = None, own_ip_netmask = None, 
                 server_address = None, udp_wait_time = _DEFAULT_UDP_WAIT_TIME,
                 port_udp = _DEFAULT_UDP_PORT, port_tcp = _DEFAULT_TCP_PORT, 
                 max_server_finding_attempts = _DEFAULT_MAX_SERVER_FINDING_ATTEMPTS, 
                 verbose_file = sys.stderr, verbosity = 0):


        if __name__ == "__main__":
            self._TAG = os.path.splitext(os.path.basename(sys.argv[0]))[0] + "." + __class__.__name__
        else:
            self._TAG = __name__ + "." + __class__.__name__
        
        if phone is None or phone.strip() == "":
            try:
                phone = os.environ[ENV_PHONE_VARIABLE]
                if verbosity > 1:
                    print("{}: Own phone ({}) retrieved from environment variable ({})".format(self._TAG, phone, ENV_PHONE_VARIABLE), file = verbose_file)        
            except KeyError:
                phone = None
        
            if phone is None or phone.strip() == "":
                raise IllegalArgumentError("Phone number is required and must be specified or given in {} environment variable".format(ENV_PHONE_VARIABLE))
        
        self._phone = phone.strip()
        if not self._phone.isdigit():
            raise IllegalArgumentError("Illegal phone number: '{}'.".format(self._phone))

        if password is None or password.strip() == "":
            try:
                password = os.environ[ENV_PASS_VARIABLE]
                if verbosity > 1:
                    print("{}: Password retrieved from environment variable ({})".format(self._TAG, ENV_PASS_VARIABLE), file = verbose_file)        
            except KeyError:
                password = None
            if password is None or password.strip() == "":
                raise IllegalArgumentError("Password is required and must be specified or given in {} environment variable".format(ENV_PASS_VARIABLE))
        
        self._password = password.strip()
        self._server_address = server_address
        self._port_udp = port_udp
        self._port_tcp = port_tcp
        self._udp_wait_time = udp_wait_time
        self._verbosity = verbosity
        self._verbose_file = verbose_file
        self._max_server_finding_attempts = max_server_finding_attempts

        if own_ip_address is None:
            self._own_ip = retrieve_own_ip()
        else:
            cidr = own_ip_address.split("/")
            self._own_ip = cidr[0]
            if len(cidr) > 1 and own_ip_netmask is None:
                own_ip_netmask = int(cidr[1])
            
        if own_ip_netmask is None:
            own_ip_netmask = retrieve_own_netmask()
            if own_ip_netmask is None:
                self._own_ip_netmask = netmask2ip(24)
            else:
                self._own_ip_netmask = own_ip_netmask
        else:
            if type(own_ip_netmask) is int:
                self._own_ip_netmask = netmask2ip(own_ip_netmask)
            else:
                self._own_ip_netmask = own_ip_netmask
        self._main_channel = None 
        pem_file = _get_pem()
        try:
            self._ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile = pem_file)
        except AttributeError:
            self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            self._ssl_context.verify_mode = ssl.CERT_REQUIRED
            self._ssl_context.load_verify_locations(pem_file)       
        
    def get_server_address(self):
        return self._server_address

    def get_own_ip(self):
        return self._own_ip
    
    def get_own_phone(self):
        return self._phone
    
    def _write(self, text):
        if self._main_channel is None:
            raise IllegalStateError("cannot write to aText server - connection is NOT open")
        print(text, file=self._main_channel)
        self._main_channel.flush()

    def _read(self):
        if self._main_channel is None:
            raise IllegalStateError("cannot read from aText server - connection is NOT open")
        return self._main_channel.readline()

    def _send_quit(self):
        command = (_ServerCommand.quit.value, )
        self._write(json.JSONEncoder().encode(command))

    def _get_response(self):
        response = json.JSONDecoder().decode(self._read())
        response_code = ServerResponseCode.create(response[0])
        response[0] = response_code
        return ServerResponse(response)
    
    def _pseudo_broadcast(self):
        if self._own_ip_netmask is None:
            return
        
        gateway_ip = retrieve_own_gateway()
        if gateway_ip is None:
            gateway_ip = ""

        for ip in all_network_ip_addresses(self._own_ip, self._own_ip_netmask):
            if ip != self._own_ip and ip != gateway_ip:            
                self._broadcast_socket.sendto(self._data2broadcast, (ip, self._port_udp))    

        if self._verbosity > 2:
            print("{}: Pseudo broadcast from {} sent: {}".format(self._TAG, self._own_ip, self._data2broadcast), file = self._verbose_file)        
        
    
    def check_sms(self):
        command = (_ServerCommand.check.value, )
        self._write(json.JSONEncoder().encode(command))
        return self._get_response()        
        
        
    def send_sms(self, send_to, text):
        command = (_ServerCommand.sms.value,{_SMS_KEY_MOBILE: send_to, _SMS_KEY_TEXT: text})
        self._write(json.JSONEncoder().encode(command))
        return self._get_response()
        
        
    def close_server_connection(self):
        if self._main_channel is not None:
            self._send_quit()
            try:
                self._main_channel.close()
            except:
                pass        
    
    def connect_to_server(self):
        self.close_server_connection()
        
        if self._server_address is None:
            raise IllegalStateError("aText server address is not set (uninitialized " + __class__.__name__ + "?)")

        server_address = (self._server_address, self._port_tcp)
        s = self._ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM));
        s.connect(server_address);
        
        self._main_channel = s.makefile("rw", encoding="utf-8")
        
        # Send invitation
        self._write(_get_magic_query_string(self._phone, self._password))
        answer = self._read().strip()
        if answer != _get_magic_response_string(self._phone):
            if answer == _prot_decode(_MAGIC_WRONG):
                raise SecurityException("aText server rejected password")
            else:
                raise SecurityException("aText server sent wrong invitation response '{}'".format(answer))
        
            
    def verify_server_presence(self, broadcast = True):
        result = False
        servers = set()
        broadcaster = None
        
        if broadcast:
            server_address = "<broadcast>"
        else:
            server_address = self._server_address
        
        if server_address is not None:
            magic_query = _get_magic_query(self._phone)
            self._data2broadcast = magic_query
            
            s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s_out.bind((self._own_ip, 0))
            if broadcast:
                s_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
            self._broadcast_socket = s_out
            
            s_in = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s_in.bind((self._own_ip, self._port_udp))
            if self._udp_wait_time > 0:
                s_in.settimeout(self._udp_wait_time)
            else:
                s_in.settimeout(_DEFAULT_UDP_WAIT_TIME)
            
            t = self._max_server_finding_attempts
            servers = set()
            do_send = True
            while t > 0:
                if do_send:
                    if (self._max_server_finding_attempts - t) % 2 == 1:
                        broadcaster = threading.Thread(target=self._pseudo_broadcast)
                        broadcaster.start()        
                    else:
                        s_out.sendto(magic_query, (server_address, self._port_udp))    
                        if self._verbosity > 2:
                            print("{}: Send: {}".format(self._TAG, magic_query), file = self._verbose_file)
                try:
                    data, addr = s_in.recvfrom(_DATAGRAM_BUFFER_SIZE)
                    
                    if broadcaster is not None:
                        broadcaster.join()
                        broadcaster = None

                    if data[0:len(_MAGIC_RESPONSE)] == _MAGIC_RESPONSE:
                        if self._verbosity > 2:
                            print("{}: Received MAGIC_RESPONSE: {}".format(self._TAG, data), file = self._verbose_file)
                        server_phone = _prot_decode(data[len(_MAGIC_RESPONSE):])
                        if self._phone == server_phone:
                            servers.add(addr[0])
                            do_send = False
                            if not broadcast:
                                t = 0
                        else:
                            if self._verbosity > 2:
                                print("{}: Received wrong _MAGIC_RESPONSE (wrong phone): {}".format(self._TAG, data), file = self._verbose_file)
                    elif data[0:len(_MAGIC_QUERY)] == _MAGIC_QUERY:
                            do_send = False
                    else:
                        print("{}: Wrong response received: {}".format(self._TAG, data), file = self._verbose_file)
                        do_send = True
                except socket.timeout:
                    if len(servers) == 0:
                        t = t - 1
                        do_send = True
                    else:
                        t = 0
            if len(servers) > 0:
                if len(servers) == 1:
                    for server in servers:
                        self._server_address = server
                        break;
                    result = True
                    if self._verbosity > 1:
                        print("{}: aText server found: {}".format(self._TAG, self._server_address), file = self._verbose_file)
                else:
                    raise TooManyServersFound(", ".join(servers))
                    
        return result
    
    def find_server(self):
        result = False
        
        if self._server_address is None:
            if self.verify_server_presence(True):
                result = True
        else:
            if self.verify_server_presence(False):
                result = True
            else:    
                if self._verbosity > 1:
                    print("{}: Cannot find aText server at address '{}'.".format(self._TAG, self._server_address), file = self._verbose_file)

        if result:
            if self._verbosity > 1:
                print("{}: aText server has been found at address '{}'.".format(self._TAG, self._server_address), file = self._verbose_file)
        
        return result



if __name__ == "__main__":
    import argparse 

    prog = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    
    parser = argparse.ArgumentParser(description = "Testing script of the asms module.", epilog="Copyright (C) 2015-2016  baseIT, http://baseit.pl")
    parser.add_argument("-s", "--server", dest = "server", help="aText server IP or name")
    parser.add_argument("-o", "--own-mobile", "--from", "--send-from", dest="telephone", metavar="SENDER_PHONE", help="sender phone number")
    parser.add_argument("-m", "--mobile", "--to", "--send-to", action="append", default=[], dest="send_to", metavar="ADDRESSEE_MOBILE", help="addressee mobile phone number")
    parser.add_argument("-p", "--pass", dest="password", metavar="PASSWORD", help="server password")
    parser.add_argument("words", default=[], nargs="*", metavar="MESSAGE_WORD", help="words of text message to send")
    parser.add_argument("-v", "--verbosity", dest = "verbosity", action="count", default=0, help="increase output verbosity")
    parser.add_argument("--version", dest = "version", action="store_true", default=False, help="print module version")
    args = parser.parse_args()

    if args.version:
        print("{}: Module version: {}".format(prog, get_version()))
        exit(0)

    
    if len(args.send_to) == 0:
        print("{}: At least one reciptient must be specified (-m option).".format(prog), file = sys.stderr)
        exit(1)
        
    if len(args.words) == 0:
        print("{}: Empty text message. Nothing to send.".format(prog), file = sys.stderr)
        exit(1)
    
    message = " ".join(args.words).strip()
    
    client = None
    try:
        client = SMS(phone = args.telephone, password = args.password, server_address = args.server, verbosity = args.verbosity)
        if not client.find_server():
            print("{}: Cannot find aText server in the local network. Exiting.".format(prog), file = sys.stderr)
            exit(1)

        print("{}: Found aText server: {}.".format(prog, client.get_server_address()))
        client.connect_to_server()

        for recipient in args.send_to:
            print("{}: Sending text to {}.".format(prog, recipient))
            response = client.send_sms(recipient, message)
            if response.is_confirmed():
                if response.has_contact_name():
                    print("{}: Text sent to {} ({}): {}.".format(prog, response.get_contact_name(), recipient, response.get_message()))
                else:
                    print("{}: OK: {}.".format(prog, response.get_message()))
            else:
                print("{}(e): Text sending error({}): {}".format(prog, response.get_code().value, response.get_message()), file = sys.stderr)
                
    except IllegalStateError as e:
        print("{}(e): Internal program error (IllegalStateError): {}.".format(prog, e), file = sys.stderr)
        exit(1)
    except SecurityException as e:    
        print("{}(e): Security error: {}.".format(prog, e), file = sys.stderr)
        exit(1)
    except Exception as e:
        print("{}(e): Execution error: {}.".format(prog, e), file = sys.stderr)
        exit(1)
    finally:    
        if not client is None:
            client.close_server_connection()
        
    exit(0)
    


