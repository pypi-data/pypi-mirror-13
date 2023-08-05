============
Najdi-si-sms
============

Command line utility to send automated sms through Slovenian Najdi.si service (40 sms per day for free).

How to use
==========


Installation
++++++++++++

You can install the package systemwide with (you need su access)::

  make install
  #or
  pip install .

You can also install the requirements with::

  pip install -r requirements.txt

If you dont want/have super user access, you can install it in a python virtual env
in the root folder call::

  virtualenv venv
  source venv/bin/activate
  pip install .

The CLI command can be found in "venv/bin/najdisi-sms" and you can add it to you PATH or call it directly.

Standalone CLI command
++++++++++++++++++++++

::

  Usage: najdisi-sms -u username -p password  RECEIVER_NUM  MESSAGE

  Options:
    -h, --help            show this help message and exit
    -u USERNAME, --username=USERNAME
                          Username
    -p PASSWORD, --password=PASSWORD
                          Password
    -A USERAGENT, --useragent=USERAGENT
                          HTTP User Agent

Example::

  najdisi-sms -u brodul -p FUBAR_PASS 031123456 "Pikica, rad te mam. (send from cronjob)"

Python API
++++++++++

Example::

  from najdisi_sms import SMSSender

  sms = SMSSender('username', 'password')
  sms.send(
      '031123456',
      'Pikica, rad te mam. (send from cronjob)'
  )
