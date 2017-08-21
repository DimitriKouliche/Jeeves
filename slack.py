# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""This allows Jeeves to communicate on Slack"""

from slackclient import SlackClient
import time
import logging
import os
from bot import speech
from bot import brain

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)
motor = brain.Motor()

if sc.rtm_connect():
    while True:
        try:
            hooks = sc.rtm_read()
            for hook in hooks:
                if 'type' in hook and hook['type'] == 'message' and 'text' in hook:
                    response = speech.respond(motor, hook['text'].lower())
                    sc.rtm_send_message(hook['channel'], response)
        except Exception as e:
            logging.exception("message")
            pass

        time.sleep(1)
else:
    logging.debug("Connection Failed, invalid token?")
