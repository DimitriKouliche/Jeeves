# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""This allows Jeeves to communicate on Slack"""

from slackclient import SlackClient
import time
import logging
import os

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)

if sc.rtm_connect():
    while True:
        logging.debug(sc.rtm_read())
        time.sleep(1)
else:
    logging.debug("Connection Failed, invalid token?")
