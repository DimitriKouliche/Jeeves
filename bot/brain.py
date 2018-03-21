# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""This module handles the brain part of Jeeves (memory, motor skills, reflexes and emotions"""
import os
import redis
import random
import operator
from textblob import TextBlob
import requests
import json
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class Utils:
    """Utils handles everything that is not related to logic."""

    @staticmethod
    def byte_string_list(byte_list):
        """Transforms a byte list to a string list
        Args:
            byte_list (list): List of bytes.
        Returns:
            list: List of strings"""
        return list(map(lambda x: x.decode("utf-8"), byte_list))


class Emotion:
    """Emotion handles everything that is related to Jeeves' feeling."""

    @staticmethod
    def feel(sentiment):
        """The feel function finds a reaction to specific sentiments felt by Jeeve' when he hears a sentence
        Args:
            sentiment (obj): An object sentiment with two properties (polarity, subjectivity).
        Returns:
            str: A reaction to the sentiment"""
        logging.info('Feeling sentiment')
        if sentiment.polarity < -0.7:
            return 'curse'


class Memory:
    """Memory handles Jeeves' memory center.
     Attributes:
         self.REDIS_DB (dict): A mapping between Redis databases IDs and memory names
         self.new_words (list): A list of the new words Jeeves discovered during the chat.
         self.redis_connections (list): A list of connections to Redis databases."""
    REDIS_DB = {"words": 0, "reactions": 1, "ignored words": 2, "new words": 3}
    new_words = []
    redis_connections = {}

    def __init__(self):
        self.create_redis_connections()

    def create_redis_connections(self):
        """Initializes redis databases connections"""
        redis_host = os.environ["REDIS_HOST"]
        for name, db in self.REDIS_DB.items():
            logging.info(f"Connecting with memory {name}")
            self.redis_connections[name] = redis.StrictRedis(host=redis_host, db=db)

    def init_memory(self, name):
        """Retrieves the Redis connection associated to a memory
        Args:
            name (str): The memory name we want to open a connection to
        Returns:
            StrictRedis: A Redis connection to the memory"""
        return self.redis_connections[name]

    def search_word(self, words):
        """Searches word known by Jeeves in a list of words
        Args:
            words (list): a list of words
        Returns:
            str|None: A reaction known by Jeeves or nothing"""
        memory = self.redis_connections['words']
        logging.info('Searching for a match among a list of words: ' + ', '.join(words))
        for word in words:
            reaction = memory.get(word)
            if reaction:
                logging.info("Found a reaction in memory")
                return reaction.decode("utf-8")
        self.new_words += words
        self.remember_new_words()

    def remember_new_words(self):
        """Stores new words in memory"""
        memory = self.redis_connections['new words']
        for word in self.new_words:
            memory.incr(word)

    def filter_ignored_words(self, words):
        """Removes words that Jeeves is supposed to ignore from a list of words
        Args:
            words (Iterator|list): a list of words
        Returns:
            list: A list of words"""
        filtered = []
        memory = self.redis_connections['ignored words']
        for word in words:
            ignore = memory.get(word)
            if ignore is None:
                filtered.append(word)
        return filtered

    def forget(self, words, memory_type):
        """Removes specific words from one of Jeeves' memories
        Args:
            words (list): a list of words
            memory_type (str): a memory name"""
        if not words:
            return
        logging.warning("Deleting these words from short term memory: " + ", ".join(words))
        memory = self.redis_connections[memory_type]
        words_tuple = tuple(words)
        memory.delete(*words_tuple)

    def ignore(self, words):
        """Adds a list of words to Jeeves' ignore list
        Args:
            words (list): a list of words"""
        if not words:
            return
        logging.warning("Adding these words to ignore memory: " + ", ".join(words))
        memory = self.redis_connections['ignored words']
        for word in words:
            memory.set(word, "useless")

    def list_all(self, memory_type):
        """Retrieves all the words contains in one of Jeeves' memories
        Args:
            memory_type (str): a memory name
        Returns:
            list: A list of words"""
        memory = self.redis_connections[memory_type]
        return Utils.byte_string_list(memory.keys())

    def add_words(self, words, memory_type, value):
        """Adds a list of words and their value in one of Jeeves' memories
        Args:
            words (list): a list of words
            memory_type (str): a memory name
            value (str): a value associated to the words"""
        memory = self.redis_connections[memory_type]
        for word in words:
            memory.set(word, value)


class Motor:
    """This class handles Jeeves' motor functions.
     Attributes:
         self.ROUTINES (dict): A mapping between some keywords and a routine Jeeves has to follow
            when he encounters them
         self.memory (Memory): Jeeves' memory center
         self.emotion (Emotion): Jeeves' emotion center
         self.hearing (Hearing): Jeeves' comprehension center"""
    ROUTINES = {"did you learn": "common_words", "please forget ": "forget_words", "please ignore ": "ignore_words",
                "list all ": "show_memory", "please add ": "memorize_word"}
    memory = Memory()
    emotion = Emotion()

    def __init__(self):
        self.hearing = Hearing(self.memory)

    def react(self, reaction):
        """Retrieve a random reaction from a list of possible reactions identified by a reaction name
        Args:
            reaction (str): a reaction name
        Returns:
            str: A random reaction"""
        logging.info("Reacting to reaction " + reaction)
        memory = self.memory.redis_connections['reactions']
        responses = memory.lrange(reaction, 0, -1)
        if responses:
            return random.choice(responses).decode("utf-8")
        logging.info("Lost connection with memory.")
        self.memory.create_redis_connections()
        return "Sorry, I had a moment of absence, could you please repeat what you were saying?"

    def check_word(self, word):
        """Checks if Jeeves knows the word. If he doesn't, searches the internet to see
            if Jeeves know a word that matches.
        Args:
            word (str): a word
        Returns:
            str|None: A random reaction"""
        logging.info("Checking word " + word)
        external = Research(self)
        intent = self.memory.search_word([word])
        if intent is None:
            words = external.research(word)
            intent = self.memory.search_word(words)
        if intent:
            return self.react(intent)

    def check_tone(self, sentiment):
        """Checks the tone of the message we sent to Jeeves to see if he can react emotionally to it
        Args:
            sentiment (obj): an object that has two properties: polarity (nice or mean)
                and objectivity (objective or subjective)
        Returns:
            str|None: A random reaction"""
        logging.info("Checking tone")
        reaction = Emotion.feel(sentiment)
        if reaction:
            return self.react(reaction)


class Routine:
    """This class handles Jeeves' routines (specific behaviors).
     Attributes:
         self.motor (Motor): Jeeves' main motor functions"""

    def __init__(self, motor):
        self.motor = motor

    def execute(self, routine_name, text):
        """Executes a routine using its name and the text Jeeves received
        Args:
            routine_name (str): the name of a routine
            text (str): the text that was sent to Jeeves
        Returns:
            str: A response set by the routine"""
        routine = getattr(self, routine_name)
        return routine(text)

    def common_words(self, text):
        """Displays the 25 most common words Jeeves has encountered when talking to people
        Args:
            text (str): the text that was sent to Jeeves (unused for now)
        Returns:
            str: A response with the list of common words separated by commas"""
        frequency = {}
        memory = self.motor.memory.redis_connections['new words']
        words = memory.keys()
        for word in words:
            frequency[word] = memory.get(word)
        sorted_words = sorted(frequency.items(), key=operator.itemgetter(1), reverse=True)
        common_words = Utils.byte_string_list([x[0] for x in sorted_words[:25]])
        return "Here's a list of the most common words I learned: " + ', '.join(common_words)

    def forget_words(self, text):
        """Makes Jeeves forget a list of words
        Args:
            text (str): the text that was sent to Jeeves (with a list of words separated by commas)
        Returns:
            str: A response with the list of words that Jeeves forgot"""
        words = text.split("forget ", 1)[1].split(', ')
        self.motor.memory.forget(words, 'new words')
        return "I forgot these words: " + ', '.join(words)

    def ignore_words(self, text):
        """Makes Jeeves ignore a list of words
        Args:
            text (str): the text that was sent to Jeeves (with a list of words separated by commas)
        Returns:
            str: A response with the list of words that Jeeves is now ignoring"""
        words = text.split("ignore ", 1)[1].split(', ')
        self.motor.memory.ignore(words)
        self.motor.memory.forget(words, 'new words')
        return "I'm now ignoring these words: " + ', '.join(words)

    def show_memory(self, text):
        """Makes Jeeves show a list of words that were stored in his memory
        Args:
            text (str): the text that was sent to Jeeves (with the name of the memory we want to access)
        Returns:
            str: A response with the list of words that Jeeves has in his memory"""
        memory_type = text.split("list all ", 1)[1]
        memories = self.motor.memory.list_all(memory_type)
        return "Here's a list of the " + memory_type + " I know: " + ', '.join(memories)

    def memorize_word(self, text):
        """Makes Jeeves memorize a word and associate it to a reaction
        Args:
            text (str): the text that was sent to Jeeves (with the name of the reaction we want to add the words
                and a list of words separated by commas)
        Returns:
            str: A response with the list of words that Jeeves has in his memory"""
        command = text.split("please add ", 1)[1]
        split = command.split(" to ", 1)
        words = split[0].split(', ')
        reaction = TextBlob(split[1]).words[0]
        self.motor.memory.add_words(words, 'words', reaction)
        return "I just associated word(s) " + ', '.join(words) + ' to my reaction "' + reaction + '".'


class Hearing:
    """This class handles Jeeves' comprehension of sentences."""

    def __init__(self, memory):
        self.memory = memory

    def get_words(self, sentence):
        """Returns a list of important words from a sentence (without ignored words)
        Args:
            sentence (str): the sentence
        Returns:
            list: A list of filtered words"""
        words = []
        text_blob = TextBlob(sentence)
        for word, pos in text_blob.tags:
            if pos[:2] in ['NN', 'VB', 'JJ']:
                words.append(word)
        filtered_words = self.memory.filter_ignored_words(filter(lambda item: item, words))
        return filtered_words

    def get_raw_words(self, sentences):
        """Returns a list of important words from a list of sentences (without ignored words)
        Args:
            sentences (list): the sentences we want to extract words from
        Returns:
            list: A list of filtered words"""
        words = []
        for sentence in sentences:
            words += self.get_words(sentence)
        return words

    @staticmethod
    def get_sentiment(sentence):
        """Returns the tone of a sentence
        Args:
            sentence (str): the sentence we want to extract the tone from
        Returns:
            obj: An object sentiment with two properties (polarity, subjectivity)"""
        text_blob = TextBlob(sentence)
        return text_blob.sentiment


class Research:
    """This class handles Jeeves' researches on the internet (when he doesn't know a word).
     Attributes:
         self.motor (Motor): Jeeves' main motor functions
         self.WORDS_API_HOST (str): Jeeves' Words API (source to query)
         self.WORDS_API_KEY (str): Jeeves' Words API key"""
    WORDS_API_HOST = "https://wordsapiv1.p.mashape.com/words/"
    WORDS_API_KEY = "1sbLJFOyD4mshxPsotSkX2bnoZ3Ep1pO0HgjsnqrMwCsc9YhOr"

    def __init__(self, motor):
        self.motor = motor

    def research(self, word):
        """Searches for a word on the internet
        Args:
            word (str): the word we want to know about
        Returns:
            list: A list of words related to the word passed in argument"""
        logging.info("Searching the web for word " + word)
        words = []
        headers = {'X-Mashape-Key': self.WORDS_API_KEY, 'Accept': 'application/json'}
        request = requests.get(self.WORDS_API_HOST + word, headers=headers)
        content = json.loads(request.content)
        if 'results' in content:
            for data in content['results']:
                words += self.analyze(data)
        return words

    def analyze(self, data):
        """Analyses a dict of data retrieved by Words API and extracts a list of words from it
        Args:
            data (dict): the data we need to parse
        Returns:
            list: A list of words related to the word passed in argument"""
        hearing = self.motor.hearing
        raw_words = self.extract_properties(data, ['typeOf', 'hasParts', 'partOf', 'instanceOf'])
        words = hearing.get_raw_words(raw_words)
        return words

    @staticmethod
    def extract_properties(data, properties):
        """Extracts properties values from a dict
        Args:
            data (dict): the data we need to parse
            properties (list): a list of properties we need to extract
        Returns:
            list: A list of words we extracted"""
        key_words = []
        for data_property in properties:
            if data_property in data:
                key_words += data[data_property]
        key_words.append(data['definition'])
        return key_words
