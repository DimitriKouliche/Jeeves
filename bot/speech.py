# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""This module handles how Jeeves responds, it's there to make the bridge between the chat and Jeeves' brain."""

from . import brain


def respond(motor, input_text):
    """Respond to a text
    Args:
        motor (Motor): Jeeves' main brain motor functions
        input_text (str): The text the user typed
    Returns:
        str: A reaction"""
    routine = search_routine(motor, input_text)
    if routine:
        return routine
    word_match = search_keyword(motor, input_text)
    if word_match:
        return word_match
    sentiment = brain.Hearing.get_sentiment(input_text)
    sentiment_match = motor.check_tone(sentiment)
    return sentiment_match or motor.react('default')


def search_keyword(motor, input_text):
    """Searches for known keywords in a text
    Args:
        motor (Motor): Jeeves' main brain motor functions
        input_text (str): The text the user typed
    Returns:
        str: A reaction"""
    important_words = motor.hearing.get_words(input_text)
    for word in important_words:
        word_match = motor.check_word(word)
        if word_match:
            return word_match


def search_routine(motor, input_text):
    """Searches for known routines in a text
    Args:
        motor (Motor): Jeeves' main brain motor functions
        input_text (str): The text the user typed
    Returns:
        str: A reaction"""
    for sentence, routine_name in motor.ROUTINES.items():
        if sentence in input_text:
            routine = brain.Routine(motor)
            return routine.execute(routine_name, input_text)
