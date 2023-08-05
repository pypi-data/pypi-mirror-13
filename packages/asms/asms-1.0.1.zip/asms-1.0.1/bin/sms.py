#!/usr/bin/python3
################################################################################
#
# Copyright (c) 2015-2016 BaseIT, http://baseit.pl
#
# Script:  sms.py 
# Version: 1.0.1
# Build:   2016.01.08 18:23:04
# Uses:    asms.py 
#
# Description:
#   Sample script designated as utility to send and receive SMS messages 
#   using API provided by the asms module.
#   Script creates and uses configuration file "sms.cfg" in user's home
#   directory. 
#
#   The following parameters can be set in the configuration file:
#     own_phone = phone_number
#     password  = password 
#     defaut_country_prefix = phone_number_prefix
#     verbosity = level_of_verbosity
#   
#   Note that password is stored in plain form to keep this sample simple.
#   In your application you should store the password in more safe way.
#   Parameter phone_number_prefix should be set to default prefix of your
#   country, such as 1 for US, 48 for Poland, 49 for Germany, 44 for UK, etc.
#
#   In addition to parameters, the configuration file stores also address book
#   in form:
#     phone_number = alias[:alias[:alias[...]]]
#
#   For example for line:
#     +44-7300000000 = John Smith:John
#   you can send texts using phone number as well as "John Smith" or John
#
#   If you send SMS to phone which is present in your mobile's contacts,
#   then your address book in the sms.cfg file is automatically updated.
#
# Usage:
#   sms.py -h
# 
# Module asms:
#   - more information: http://baseit.pl/#product-asms
#   - installation:     pip install asms
#
# This script may be downloaded, installed, run and used in accordance with 
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
import asms

import sys
import os
import argparse
import fileinput
import re

prog = os.path.splitext(os.path.basename(sys.argv[0]))[0]

SMS_DATETIME_FORMAT = "%H:%M:%S %d.%m.%Y"
DEFAULT_UDP_WAIT_TIME = 1

CONFIG_OWN_PHONE              = "own_phone"
CONFIG_PASSWORD               = "password"
CONFIG_VERBOSITY              = "verbosity"
CONFIG_DEFAULT_COUNTRY_PREFIX = "default_country_prefix"

def main():
    global verbosity
    
    if args.version:
        print("{}: asms module version: {}, build: {} ({} netifaces).".format(prog, 
            asms.get_version(), asms.get_build_date(), 
            "using" if asms.using_netifaces() else "without"))
        return(0)
    
    try:
        config = Configuration(prog)
        phone = config.get_parameter(CONFIG_OWN_PHONE)
        password = config.get_parameter(CONFIG_PASSWORD)
        verbosity = int(config.get_parameter(CONFIG_VERBOSITY, 0))
    
        receive_sms_only = args.read_only    
                
        if args.verbosity > 0:
            verbosity = args.verbosity
            
        if not args.password is None:
            password = args.password
        
        if not args.telephone is None:    
            phone = args.telephone    
                        
        try:
            client = asms.SMS(phone = phone, password = password, server_address = args.server, verbosity = verbosity, udp_wait_time = args.wait)
            if not client.find_server():
                print("{}(e): Cannot find aText server in the local network. Exiting.".format(prog), file = sys.stderr)
                return(1)
    
            if args.verbosity > 0:
                print("{}: Found aText server: {}.".format(prog, client.get_server_address()))
    
        except asms.IllegalArgumentError as e:
            print("{}(e): Argument error: {}".format(prog, e), file = sys.stderr)
            return(1)
    
        except asms.TooManyServersFound as e:
            print("{}(e): More than 1 server found ({}). Possible security problem.".format(prog, e), file = sys.stderr)
            return(1)
    
        if not receive_sms_only:
            if len(args.send_to) == 0:
                if verbosity > 0:
                    print("{}: Empty addressees list. Nothing to do.".format(prog))
                return(0)
    
            if len(args.words) == 0:
                message = "".join(fileinput.input("-"))
            else:
                message = " ".join(args.words)
    
            if message is None or len(message.strip()) == 0:
                if verbosity > 0:
                    print("{}: Empty message. Nothing to do.".format(prog))
                return(0)
            
        try:
            client.connect_to_server()
    
            if receive_sms_only:
                all_messages_received = False
                while not all_messages_received:
                    response = client.check_sms()
                    if response.is_confirmed():
                        try:
                            r_msg = response.get_sms_message()
                            r_sent_from = response.get_sent_from()
                            r_receive_time = response.get_receive_time()
                            r_smsc_time = response.get_smsc_time()
                            
                            if response.has_contact_name():
                                r_sender_contact = response.get_contact_name()
                                config.put_contact(r_sent_from, r_sender_contact)
                                r_sender = r_sender_contact + " (" + r_sent_from + ")"
                            else:
                                r_sender = r_sent_from
                            if verbosity > 2:
                                print("{}: Text from {} sent at {}, and received at {}".format(prog, safe_encode(r_sender), r_smsc_time, r_receive_time))
                            print("{}: {}".format(safe_encode(r_sender), safe_encode(r_msg)))
                            print();
                        except KeyError as e:
                            print("{}(e): Wrong data received (KeyError): {}.".format(prog, e), file = sys.stderr)
                    elif response.is_rejected():
                        all_messages_received = True
                        if verbosity > 0:
                            print("{}: No more text messages available.".format(prog), file = sys.stderr)
                    else:
                        print("{}(e): Text receiving error({}): {}".format(prog, response.get_code().value, response.get_message), file = sys.stderr)
                
            else:
                message = message.strip()
                
                if len(args.send_to) > 0 and len(message) > 0:
                    for addressee in args.send_to:
                        addressee_label = addressee
                        if addressee[1].isalpha():
                            addressee_phone = config.get_phone(addressee)
                            if addressee_phone is None:
                                print("{}(e): Unknown phone for contact '{}'.".format(prog, addressee), file = sys.stderr)
                                continue
                            else:
                                addressee_label = "{} <{}>".format(addressee, addressee_phone)
                                addressee = addressee_phone
                        if verbosity > 0:
                            print("{}: Sending text to {}: '{}'.".format(prog, addressee_label, safe_encode(shorten(message, 40))))
                        response = client.send_sms(addressee, message)
                        if response.is_confirmed():
                            if response.has_contact_name():
                                addressee_contact = response.get_contact_name()
                                config.put_contact(addressee, addressee_contact)
                                if verbosity > 0:
                                    print("{}: Text sent to {} ({}): {}.".format(prog, addressee_contact, addressee, response.get_message()))
                            else:
                                if verbosity > 0:
                                    print("{}: OK: {}.".format(prog, response.get_message()))
                        else:
                            print("{}(e): Text sending error({}): {}".format(prog, response.get_code().value, response.get_message()), file = sys.stderr)
                    
        except asms.IllegalStateError as e:
            print("{}(e): Internal program error (IllegalStateError): {}.".format(prog, e), file = sys.stderr)
            return(1)
        except asms.SecurityException as e:    
            print("{}(e): Security error: {}.".format(prog, e), file = sys.stderr)
            return(1)
        except Exception as e:
            print("{}(e): Execution error: {}.".format(prog, e), file = sys.stderr)
            return(1)
        finally:    
            client.close_server_connection()
            if not config.has_preferences():
                config.put_parameter(CONFIG_OWN_PHONE, client.get_own_phone())
                config.put_parameter(CONFIG_PASSWORD, None)
                config.put_parameter(CONFIG_VERBOSITY, 1)
                config.put_parameter(CONFIG_DEFAULT_COUNTRY_PREFIX, None)
            config.save()
    
    except ConfigurationFileError as e:
        print("{}(e): Configuration error: {}.".format(prog, e), file = sys.stderr)
        return(1)
    except Exception as e:
        print("{}(e): Generic error: {}.".format(prog, e), file = sys.stderr)
        return(1)
    
    return(0)


def safe_encode(input_string):
    code_page = sys.stdout.encoding
    return(input_string.encode(code_page, "ignore").decode(code_page, "ignore"))

def shorten(text, required_length):
    if text is None:
        return ""
    if len(text) <= required_length:
        return text
    return text[:required_length - 3] + "..."

_CFG_FILE_EXTENSION = "cfg"
_COMMENTS_TAGS = ["#", "//"]

class ConfigurationFileError(Exception):
    pass

class Configuration:
    def __init__(self, file_name):
        if file_name is None:
            raise ValueError("Configuration file_name must be specified")
            
        self._address_book = {}
        self._phone_book = {}
        self._preferences = {}
        self._is_modified = False
            
        home = os.path.expanduser("~")
        self._config_file_path = os.path.join(home, file_name + os.extsep + _CFG_FILE_EXTENSION)

        line_number = 0
        try:
            with open(self._config_file_path, encoding="utf-8") as f:
                for line in f:
                    line_number = line_number + 1
                    self._process_line(line, line_number)
        except IOError:
            pass # Configuration file is optional

    def _process_line(self, line, line_number):
        line = line.strip()
        
        if len(line) == 0 or any(line.startswith(comment) for comment in _COMMENTS_TAGS):
            return

        c = line[0]
        if c.isalpha():
            pref_key, sep, pref_value = line.partition("=")
            self._preferences[pref_key.strip().lower()] = pref_value.strip()
        elif c == "+" or c.isdigit():
            phone, sep, phone_contacts = line.partition("=")
            phone = self.normalize_phone(phone)
            current_contacts = set()
            for contact in phone_contacts.split(":"):
                family_name, sep, first_name = contact.partition(",")
                contact = " ".join((first_name + " " + family_name).lower().split())
                self._address_book[contact] = phone
                current_contacts.add(contact)

            self._phone_book[phone] = current_contacts
                
        else:
            raise ConfigurationFileError("wrong line (#{}) in configuration file {}".format(line_number, self._config_file_path))

    def normalize_phone(self, phone):
        phone = phone.strip()
        
        if not phone.startswith("+"):
            try:
                phone = "+" + self._preferences[CONFIG_DEFAULT_COUNTRY_PREFIX] + phone
            except KeyError:
                pass
                
        return(re.sub("[\s-]*", "", phone))
            
    def _line_has_preference(self, preference_key, line):
        line = line.strip().lower()

        if len(line) == 0 or any(line.startswith(comment) for comment in _COMMENTS_TAGS):
            return(False)
        
        if line[0].isalpha():
            actual_preference_key, sep, actual_preference_value = line.partition("=")
            if actual_preference_key.strip() == preference_key:
                return(True)
            
        return(False)

    def _line_has_phone(self, phone, line):
        line = line.strip().lower()

        if len(line) == 0 or any(line.startswith(comment) for comment in _COMMENTS_TAGS):
            return(False)

        c = line[0]    
        if c == "+" or c.isdigit():
            actual_phone, sep, actual_contacts = line.partition("=")
            if self.normalize_phone(actual_phone) == phone:
                return(True)
            
        return(False)
        
        
    def put_contact(self, phone, contact):
        contact = contact.lower()
        phone = self.normalize_phone(phone)
        if contact not in self._address_book:
            self._is_modified = True
            self._address_book[contact] = phone
            if phone in self._phone_book:
                phone_contacts = self._phone_book[phone]
                phone_contacts.add(contact)
                self._phone_book[phone] = phone_contacts
            else:
                self._phone_book[phone] = {contact}

    @staticmethod
    def format_phone(phone):
        n = 3
        plus = ""
        if phone.startswith("+"):
            plus = "+"
            phone = phone[1:]
        
        l = (n - len(phone) % n) % n
        src = " " * l + phone
        
        return(plus + "-".join(src[i:i+n] for i in range(0, len(src), n)).strip())        
            
    def create_empty_file(self):
        return
        
    def save(self, force_save = False):
        if self._is_modified or force_save:
            try:
                if not os.path.isfile(self._config_file_path):
                    header = ['SMS configuration file (for: {})'.format(os.path.realpath(__file__)),
                              'This file contains configuration parameters (parameter = value) and',
                              'address book given in the following syntax:',
                              'phone_number = alias[:alias[...]]',
                              '(i.e. phone_number followed by "=" and list of aliases separated by ":")']
                    with open(self._config_file_path, 'a') as f:
                        for l in header:
                            print("# {}".format(l), file = f)
                        print("\n", file = f)

                    print("{}: Configuration file has been created: {}.".format(prog, self._config_file_path))
                    
                    
                f = open(self._config_file_path, "r+", encoding="utf-8")
                lines = f.readlines()
                
                for preference_key in self._preferences.keys():
                    preference_updated = False
                    new_value = self._preferences[preference_key]
                    if new_value is None:
                        new_line = "# {} = ".format(preference_key) + "\n"
                    else:
                        new_line = preference_key + " = " + str(new_value) + "\n"
                    for n, l in enumerate(lines):
                        if self._line_has_preference(preference_key, l):
                            lines[n] = new_line
                            preference_updated = True
                            break
                    if not preference_updated:
                        lines.append(new_line)
                
                
                for phone in self._phone_book.keys():
                    phone_updated = False
                    new_line = Configuration.format_phone(phone) + " = " + ":".join(self._phone_book[phone]).title() + "\n" 
                    for n, l in enumerate(lines):
                        if self._line_has_phone(phone, l):
                            lines[n] = new_line
                            phone_updated = True
                            break
                    if not phone_updated:
                        lines.append(new_line)
                
                f.seek(0, 0)
                f.writelines(lines)
                f.close()
                
            except IOError as e:
                raise ConfigurationFileError("cannot save configuration file {}: {}".format(self._config_file_path, e.strerror))

    
    def get_preferences(self):
        return self._preferences
    
    def has_preferences(self):
        return bool(self._preferences)
        
    def get_contacts(self):
        return self._address_book

    def get_parameter(self, key, default_value = None):
        try:
            return self._preferences[key.lower()]
        except KeyError:
            return default_value

    def put_parameter(self, key, new_value):
        self._is_modified = True
        if new_value is None:
            if not key.lower() in self._preferences:
                self._preferences[key.lower()] = None
        else:
            self._preferences[key.lower()] = new_value
            
            
    def get_phone(self, contact):
        try:
            return self._address_book[contact.lower()]
        except KeyError:
            return None
    
class ActionCountValue(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):
        argparse.Action.__init__(self, option_strings=option_strings, dest=dest, nargs=nargs, const=const, default=default, type=type, choices=choices,
                                 required=required, help=help, metavar=metavar)
        return

    def __call__(self, parser, namespace, values, option_string=None):
        current = getattr(namespace, self.dest, 0)
        
        try:
            if values is None:
                current += 1
            else:
                if isinstance(values, list):
                    for v in values:
                        current += int(v)
                else:
                    current += int(values)
        except ValueError as e:
            raise argparse.ArgumentError(self, "option must have integer value if any") 

        setattr(namespace, self.dest, current)    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "SMS client designated to send text messages through aText mobile application.", epilog="Copyright (C) 2015-2016  baseIT, http://baseit.pl")
    parser.add_argument("-o", "--own-mobile", "--from", "--send-from", dest="telephone", metavar="SENDER_PHONE", help="sender phone number")
    parser.add_argument("-p", "--pass", dest="password", metavar="PASSWORD", help="server password")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m", "--mobile", "--to", "--send-to", action="append", default=[], dest="send_to", metavar="ADDRESSEE_MOBILE", help="addressee mobile phone number")
    group.add_argument("-r", "--read", action="store_true", default=False, dest="read_only", help="read received text messages (if any)")
    parser.add_argument("words", default=[], nargs="*", metavar="TEXT_WORD", help="words of text message to send")
    parser.add_argument("-v", "--verbosity", "--verbose", dest="verbosity", action=ActionCountValue, default=0, nargs="?", help="increase output verbosity", metavar="LEVEL")
    parser.add_argument("-s", "--server", dest = "server", help="aText server IP or name")
    parser.add_argument("-w", "--wait", type=int, default=DEFAULT_UDP_WAIT_TIME, help="UDP socket wait time (seconds)")
    parser.add_argument("--version", action="store_true", default=False, dest="version", help="show version of the asms module")
    args = parser.parse_args()
    
    rc = main()

    exit(rc)
