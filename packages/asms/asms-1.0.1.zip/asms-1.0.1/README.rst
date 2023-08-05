==============
asms 1.0.1
==============

The **asms** module provides functionality of SMS sending and receiving via
mobile phone. To be more specific, **asms** module act as a client of mobile
application **aText** (http://baseit.pl/#product-aText), running on mobile 
phone connected through WiFi to the same local network as machine running 
Python script.

.. contents::
   :depth: 2
   
Dependencies
------------

	- Module `enum34 <https://pypi.python.org/pypi/enum34>`_ 
	  for installations targeted to Python version below 3.4,
	  
	- There are no dependencies for installations targeted to Python 3.4 and above.
	
	- Installation of module 
	  `netifaces <https://pypi.python.org/pypi/netifaces>`_ is recommended. 
	  This module is used when available.	

	  
Overview
--------

	Module provides SMS interface, enabling scripts to send and receiving text
	messages (SMSes) via mobile application aText. The aText application must
	be running on the mobile phone (under Android), which is connected to the
	same WLAN (WiFi) as machine that runs Python script using asms module.
	
	Text messages are actually sent and received by aText mobile application
	(http://baseit.pl/#product-aText) running on user's mobile phone and 
	therefore all related fees are charged by a telecommunications operator,
	which provides services to the user. Neither program texting nor mobile
	application aText interfere with billing or rating of text messages by 
	the telco operator. In other words, sending or receiving a text message
	using program texting and via mobile application aText, should cost the
	same as sending or receiving a similar text message directly on user's
	mobile phone.
	
	Mobile application aText (available under commercial, separate license) can
	be obtained here: http://baseit.pl/#dload-atext
	
	Android is a trademark of Google Inc.
	
.. note::
	Although network communication between asms module and mobile
	application aText is encrypted (SSL), this software is NOT intended to be
	used for applications requiring a high level of security, therefore please
	do NOT use this software for such kind of applications (e.g. for banking,
	etc.). Sent text messages are not encrypted, i.e. text messages are sent
	from a mobile application aText in the same way as directly from the mobile
	phone.

	
Downloading and installation
----------------------------

The recommended way of the module downloading and installation is to use pip:

.. code-block:: bash
	
	$ pip install asms
	
Module installation package can be also downloaded from: http://baseit.pl/#product-asms
and installed:

.. code-block:: bash
	
	$ pip install asms-1.0.1-py3-none-any.whl
	$ pip install asms-1.0.1.zip

	
How to use - quick start
------------------------

Module asms needs only two basic parameters to send or receive SMSes:

	- password (the same as set in set for mobile application aText).
		  Password may be provided as parameter during instantiation of 
		  asms.SMS class or as asms. ENV_PASS_VARIABLE environment 
		  variable ("SMSPASS"), and
		  
	- own phone number (number of mobile phone running application aText).
		  Own phone number may be provided as parameter during instantiation of
		  asms.SMS class or as asms. ENV_PHONE_VARIABLE environment variable
		  ("SMSPHONE").
	
The asms module broadcasts LAN and automatically finds mobile phones running 
aText application connected to the same LAN segment through WiFi, and set up 
for the same "own phone number". Note, that only one aText application with
the given "own phone number" can be active in the local network segment. 

Most of work is performed by asms.SMS class in the following, typical steps:

	1. Instantiate the class:
		.. code-block:: python
		
			client = asms.SMS(own_phone, password)
	2. Find mobile phone running application aText:
		.. code-block:: python
		
		   if client.find_server():
	3. If server has been found, then we can connect to the aText application:
		.. code-block:: python
		
		   client.connect_to_server()
	4. Now, we can send SMS:
		.. code-block:: python
		
		   response = client.send_sms(recipient_phone, message)
	5. ... and / or receive SMS-es (if any):
		.. code-block:: python
		
		   response = client.check_sms()
		   if response.is_confirmed():
			   print(response.get_sms_message())
	6. Close connection:
		.. code-block:: python
		
		   client.close_server_connection()

		   
Basic usage pattern - sending SMS
=================================

Below you can find complete, basic sample of sending SMS using asms module:

.. code-block:: python

	import asms
	import sys

	OWN_PHONE_NUMBER = "..."
	ATEXT_APPLICATION_PASSWORD = "..."
	RECIPIENT_PHONE_NUMBER = "..."
	MESSAGE_TO_SEND = 'Hello World!'

	client = None
	try:
		client = asms.SMS(phone = OWN_PHONE_NUMBER, password = ATEXT_APPLICATION_PASSWORD)
		if client.find_server():
			print("Found aText server: {}.".format(client.get_server_address()))
		else:
			print("Cannot find aText server in the local network. Exiting.", file = sys.stderr)
			exit(1)

		client.connect_to_server()

		response = client.send_sms(RECIPIENT_PHONE_NUMBER, MESSAGE_TO_SEND)
		if response.is_confirmed():
			print("OK: {}.".format(response.get_message()))
		else:
			print("Text sending error({}): {}".format(response.get_code().value, response.get_message()), file = sys.stderr)
				   
	except Exception as e:
		print("Execution error: {}.".format(e), file = sys.stderr)
		exit(1)
	finally:    
		if not client is None:
			client.close_server_connection()

	exit(0)
	
	
Basic usage pattern - reading SMS(es)
=====================================

Below you can find template code of complete, basic sample of receiving
SMS using asms module. 

This sample is based on assumption that own phone number and password are
set in environment variables: **SMSPHONE** and  **SMSPASS**  respectively.

.. code-block:: python

    import asms
    import sys

    client = None
    try:
        client = asms.SMS()
        if client.find_server():
            print("Found aText server: {}.".format(client.get_server_address()))
        else:
            print("Cannot find aText server in the local network. Exiting.", file = sys.stderr)
            exit(1)

        client.connect_to_server()
        
        while True:
            r = client.check_sms()
            if r.is_confirmed():
                if r.has_contact_name():
                    sender = "{} ({})".format(r.get_contact_name(), r.get_sent_from())
                else:
                    sender = r.get_sent_from()
                print("Text from {} sent at {}, and received at {}".format(sender, r.get_smsc_time(),r.get_receive_time()))
                print(r.get_sms_message())
            elif response.is_rejected():
                break
            else:
                print("Text receiving error({}): {}".format(response.get_code().value, response.get_message), file = sys.stderr)
    except Exception as e:
        print("Execution error: {}.".format(e), file = sys.stderr)
        exit(1)
    finally:    
        if not client is None:
            client.close_server_connection()

    exit(0)

	
Using the asms Module
---------------------

asms Constants
==============

asms.ENV_PASS_VARIABLE = "SMSPASS"
##################################
	Name of the environment variable which is expected to provide password, 
	if not set as parameter during instantiation of asms.SMS class.
	
asms.ENV_PHONE_VARIABLE = "SMSPHONE"
####################################
	Name of the environment variable which is expected to provide own phone number,
	if not set as parameter during instantiation of asms.SMS class.

asms Exceptions
===============

*exception* asms.IllegalArgumentError
#####################################
	A subclass of ValueError raised when method is invoked with invalid arguments.
	For example exception asms.IllegalArgumentError is raised when invalid phone
	number is passed as parameter to asms.SMS class.
  
*exception* asms.IllegalStateError
##################################
	A subclass of ValueError raised when state of the module and / or environment
	prohibits further processing. For example asms.IllegalStateError is raised
	if asms.get_own_ip function cannot determine own ip address.

*exception* asms.SecurityException
##################################
	Raised when application security is violated, for example when provided
	password is rejected by aText mobile application for given own phone number.

*exception* asms.TooManyServersFound(SecurityException)
#######################################################
	A subclass of SecurityException raised when more than one valid aText mobile
	application is detected for given own phone number.

asms Classes
============

*class* asms.ServerResponseCode
###############################

Enum class providing values of possible SMS server (aText application)
response codes:

- confirmed
	  means, that server confirmed the request (e.g. SMS has been sent),
	  
- rejected
	  means, that server rejected the request (e.g. there is no more SMS-es
	  to read),
	  
- error
	  means, that the request has not been performed and server reports error.

		  
*class* asms.ServerResponse
###########################

The ServerResponse class provides server (aText application) response and
information, such as response code (*get_code()*) and 
server message (*get_message()*) describing response.

get_code()
^^^^^^^^^^
	Returns actual response code as an instance of 
	asms.ServerResponseCode class.
	
get_message()
^^^^^^^^^^^^^
	Returns additional text describing response as returned from
	the server (aText application).
	
	Instead of using get_code() one should use methods: 
	is_confirmed(), is_rejected(), is_error()

is_confirmed()
^^^^^^^^^^^^^^
	Returns True if get_code() == asms.ServerResponseCode.confirmed

is_rejected()
^^^^^^^^^^^^^
	Returns True if get_code() == asms.ServerResponseCode.rejected

is_error()
^^^^^^^^^^
	Returns True if get_code() == asms.ServerResponseCode.error
	When reading SMS-es (instance of asms.ServerResponce class is returned 
	from the check_sms method of the SMS class object) the following
	methods can be used:

has_sms_message()
^^^^^^^^^^^^^^^^^
	Returns True if response contains text of SMS message.
	
get_sms_message()
^^^^^^^^^^^^^^^^^
	Returns text of SMS message.
	
has_sent_from()
^^^^^^^^^^^^^^^
	Returns True if response contains phone number of the sender of the
	SMS message.
	
get_sent_from()
^^^^^^^^^^^^^^^
	Returns phone number of the sender of the SMS message.
	
has_smsc_time()
^^^^^^^^^^^^^^^
	Returns True if response contains timestamp when the SMS was registered
	by the telco operator, i.e.in the SMSC (SMS Center).
	
get_smsc_time()
^^^^^^^^^^^^^^^
	Returns timestamp when the SMS was registered by the telco operator,
	i.e.in the SMSC (SMS Center).
	
has_receive_time()
^^^^^^^^^^^^^^^^^^
	Returns True if response contains timestamp when the SMS was received
	by the mobile phone (aText application).
	
get_receive_time()
^^^^^^^^^^^^^^^^^^
	Returns timestamp when the SMS was received by the mobile phone
	(aText application).

	
Additionally, one can check if server returned contact name of the
SMS peer phone number basing on mobile phone contacts directory.
	
has_contact_name()
^^^^^^^^^^^^^^^^^^
	Returns True if response contains contact name of the SMS
	peer (sender when receiving SMS or recipient when sending SMS).
	Contact name is retrieved from the contacts directory of
	mobile phone used.
	
get_contact_name()
^^^^^^^^^^^^^^^^^^
	Returns contact name of the SMS peer (sender when receiving SMS
	or recipient when sending SMS) as provided by the server
	(application aText). Contact name is retrieved from the contacts
	directory of mobile phone used.

	
*class* asms.SMS
################

The SMS client class providing interface to send and receive text messages
(SMS-es).

asms.SMS(phone = None, password = None, own_ip_address = None, own_ip_netmask = None, server_address = None, udp_wait_time = 1, port_udp = 1410, port_tcp = 1410, max_server_finding_attempts = 16, verbose_file = sys.stderr, verbosity = 0)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	Creates a new SMS client. 
	Although all of parameters are optional, providing 
	**phone** and **password** values is strongly recommended.
			
	phone = None
		Own phone number, i.e. phone number of the user's mobile phone on which
		aText mobile application is running and which will be used actually to
		send text messages (SMS-es) from. Default value is None which instruct
		the SMS client to attempt retrieving actual own phone number from
		environment variable **SMSPHONE**.
	
	password = None
		Password of aText mobile application. Default value is None which
		instruct the SMS client to attempt retrieving actual own phone number
		from environment variable **SMSPASS**.
		
	own_ip_address = None
		Own IPv4 address of the network interface which should be used to
		communicate to the mobile phone (aText mobile application) through
		WLAN / WiFi network. Default value None means that own IPv4 address
		is determined by the SMS client. If own_ip_address parameter
		is provided in CIDR notation (e.g. '192.100.100.100/24' for netmask
		'255.255.255.0'), then own_ip_netmask is determined basing on network
		part of the address.
		
	own_ip_netmask = None
		Own IPV4 network mask. Can be provide provided in both dot-decimal
		and bits number format (e.g. '255.255.255.0' and 24 respectively).
		Default value None means that own IPv4 network mask is determined by
		the SMS client:	

		- if own_ip_address is provided in CIDR notation and contains
		  network part (e.g. 24 for '192.100.100.100/24') then network
		  part is used to compute network mask;
		  
		- else if module netifaces is installed and available then actual
		  network mask is retrieved using netifaces;
		  
		- else value 24 is assumed (i.e. network mask: '255.255.255.0').
			
		Skipping this parameter (or providing None value) is recommended,
		If netinet module is installed and available.

	server_address = None	
		If mobile phone (aText mobile application) IPv4 WiFi address is known
		and fixed, then it can be used to avoid broadcast and skip searching
		of the mobile phone in the local network. Default value None directs
		SMS client to search for mobile phone running aText application in
		the local network.
	
	udp_wait_time = 1
		Number of seconds to wait for mobile phone answer during basic attempt
		of local network searching.
		
	port_udp = 1410
		UDP port used. Parameter should NOT be used nor changed in the current
		version (1.0.1) of the asms module.
		
	port_tcp = 1410
		TCP port used. Parameter should NOT be used nor changed in the current
		version (1.0.1) of the asms module.
		
	max_server_finding_attempts = 16
		How many finding attempts should the asms modul to take before
		giving up.
		
	verbose_file = sys.stderr
		Where output of SMS client messages should be directed.
		
	verbosity = 0
		Level of SMS client verbosity. Default value 0 means minimal
		level of verbosity (no messages at all). Maximum value is 3.
	
	
connect_to_server()
^^^^^^^^^^^^^^^^^^^
	Connects SMS client to the server (mobile phone on which aText mobile
	application is running). Raises SecurityException if server rejects
	connection because of invalid password. 
	Appropriate socket.error / OSError can be raised in case occurrence
	of network communication problems.

send_sms(send_to, text)
^^^^^^^^^^^^^^^^^^^^^^^
	Sends text as SMS (text message) to send_to phone number.
	Returns response as object of asms.ServerResponse class.
	If SMS is successfully sent then response.is_confirmed() == True. 
	Appropriate socket.error / OSError can be raised in case occurrence
	of network communication problems.

check_sms()
^^^^^^^^^^^
	Reads SMS (text message) if available in the mobile phone 
	(on which aText mobile application is running). 
	Returns response as object of asms.ServerResponse class. 
	If SMS is read then response.is_confirmed() == True. 
	If no more SMS messages are available to be read 
	then response.is_rejected() == True. 
	Appropriate socket.error / OSError can be raised in case occurrence
	of network communication problems.

find_server()
^^^^^^^^^^^^^
	Find server (mobile phone on which aText mobile application is running)
	in the local network. 
	Returns True if mobile phone is found, False otherwise.

close_server_connection()
^^^^^^^^^^^^^^^^^^^^^^^^^
	Closes network connection to server (mobile phone on which 
	aText mobile application is running). 
	
	This method should be be invoked from within finally clause of
	the try block enclosing SMS client construction, 
	connection and interaction:
	
	.. code-block:: python

		import sys
		import asms
		
		client = None
		try:
			client = asms.SMS()
			if client.find_server():
				client.connect_to_server()
				while True:
					r = client.check_sms()
					if r.is_confirmed():
						print(r.get_sms_message())
		except Exception as e:
			print("Execution error: {}.".format(e), file = sys.stderr)
			exit(1)
		finally:    
			if not client is None:
				client.close_server_connection()
				
get_own_ip()
^^^^^^^^^^^^
	Returns own IPv4 address.
	
get_own_phone()
^^^^^^^^^^^^^^^
	Returns own phone, i.e.  phone number of the user's mobile phone on
	which aText mobile application is running and which will be used
	actually to send text messages (SMS-es) from.
	
get_server_address()
^^^^^^^^^^^^^^^^^^^^
	Return server (mobile phone on which aText mobile application is
	running) IPv4 address if is already known or None.
		
asms Functions
==============

asms.get_version()
##################

	Returns version of the asms module, i.e. string '1.0.1' 
	for the current version.

asms.get_build_date()
#####################

	Returns string contains build date of the module (i.e. string '2016.01.08 18:23:04') 
	for the current build.
	
	
asms.using_netifaces()
######################

	Returns True if **netifaces** module is installed in the user's
	environment and is imported and can be used.
	
	
asms.get_main_network_interface_id()
####################################

	If netifaces module is installed returns main network interface id
	(e.g. 'eth0'), otherwise returns None. 
	Helper function which is used internally by the module.
	
	
asms.get_main_network_interface()
#################################

	If netifaces module is installed main returns main network interface
	(as defined by netifaces), otherwise returns None. 
	Helper function which is used internally by the module.
	
	
asms.retrieve_own_ip()
######################

	Returns IPv4 address (in dot-decimal notation) of the given machine. 
	If netifaces module is installed and available then ip address of the main
	interface is returned, otherwise for computer with more than one network
	interface, this function should return address of one of interfaces which
	provides connection to the Internet. 
	Raises exception IllegalStateError if own IPv4 address cannot be 
	determined. Helper function which is used internally by the module.
	
	
asms.retrieve_own_netmask()
###########################

	If netifaces module is installed and available, returns own network mask 
	(in dot-decimal notation) of the given machine. Otherwise returns None. 
	Helper function which is used internally by the module.


asms.retrieve_own_gateway()
###########################

	If netifaces module is installed and available, returns own IPv4 address
	of default gateway (in dot-decimal notation) of the given machine. 
	Otherwise returns None. 
	Helper function which is used internally by the module.
	
	
asms.netmask2ip(netmask_bits)
#############################

	Converts number of bits specified in netmask_bits parameter to network mask
	with leftmost netmask_bits set to b'1' and returns IPv4 network mask in
	dot-decimal notation (e.g.'255.255.255.0' for netmask_bits == 24). 
	Raises IllegalArgumentError exception if netmask_bits value is 
	out of range <1, 31>. 
	Helper function which is used internally by the module. 
	
	
asms.ip2b(dot_address)
######################

	Converts IPv4 address from dot-decimal notation (e.g."192.100.100.100") 
	to binary integer. Returns IPV4 address in binary, integer format. 
	Helper function which is used internally by the module. 
	
	
asms.b2ip(bin_address)
######################

	Converts IPv4 address from binary integer to dot-decimal notation 
	(e.g."8.8.8.8"). Returns IPV4 address in dot-decimal notation. 
	Helper function which is used internally by the module.
	
	
asms.all_network_ip_addresses(dot_ip, dot_netmask)
##################################################

	Returns list of all valid IPv4 addresses of the given IPv4 subnetwork. 
	Subnetwork is computed basing on IPv4 address (dot_ip) and network mask
	(dot_netmask) which must be provided in dot-decimal notation. 
	Helper function which is used internally by the module.

Sample script
-------------

sms.py
======
The sms.py is a sample script designated as utility to send and receive 
SMS messages using API provided by the **asms** module. This script can
be examined as recommended sample of the asms module usage for sending
and receiving text messages.

Script Usage:

.. code-block:: bash

	$ sms.py -h	
	
	usage: sms.py [-h] [-o SENDER_PHONE] [-p PASSWORD] [-m ADDRESSEE_MOBILE | -r]
				  [-v [LEVEL]] [-s SERVER] [-w WAIT] [--version]
				  [TEXT_WORD [TEXT_WORD ...]]

	SMS client designated to send text messages through aText mobile application.

	positional arguments:
	  TEXT_WORD             words of text message to send

	optional arguments:
	  -h, --help            show this help message and exit
	  -o SENDER_PHONE, --own-mobile SENDER_PHONE, --from SENDER_PHONE, --send-from SENDER_PHONE
							sender phone number
	  -p PASSWORD, --pass PASSWORD
							server password
	  -m ADDRESSEE_MOBILE, --mobile ADDRESSEE_MOBILE, --to ADDRESSEE_MOBILE, --send-to ADDRESSEE_MOBILE
							addressee mobile phone number
	  -r, --read            read received text messages (if any)
	  -v [LEVEL], --verbosity [LEVEL], --verbose [LEVEL]
							increase output verbosity
	  -s SERVER, --server SERVER
							aText server IP or name
	  -w WAIT, --wait WAIT  UDP socket wait time (seconds)
	  --version             show version of the asms module

	Copyright (C) 2015-2016 baseIT, http://baseit.pl

sms.cfg
=======
Script creates and uses configuration file "sms.cfg" in user's home
directory. 

The following parameters can be set in the configuration file:

::

	own_phone = phone_number
	password  = password
	defaut_country_prefix = phone_number_prefix
	verbosity = level_of_verbosity

Note that password is stored in plain form to keep this sample simple.
In your real application you should store the password in more safe way.

Parameter phone_number_prefix should be set to default prefix of your
country, such as 1 for US, 48 for Poland, 49 for Germany, 44 for UK, etc.

In addition to parameters, the configuration file stores also address book
in form:

::

	phone_number = alias[:alias[:alias[...]]]

For example for line:

::

	+44-7300000000 = John Smith:John

you can send texts using phone number as well as "John Smith" or John.

If you send SMS to phone which is present in your mobile's contacts,
then your address book in the *sms.cfg* file is automatically updated.



	
License
-------
The asms module may be downloaded, installed, run and used in accordance with
the terms of the MIT license:

	**Copyright (c) 2015-2016 BaseIT**

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in
	all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
	OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
	FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
	DEALINGS IN THE SOFTWARE.

.. note::
	Even though asms module is licensed under MIT license and thus may be
	used for free, the mobile application aText is licensed on a commercial
	basis, and its use is covered by a separate and distinct license agreement.

	