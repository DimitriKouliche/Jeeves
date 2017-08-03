import redis
import random
import operator
from textblob import TextBlob
from bot import external


class Utils:
    @staticmethod
    def byte_string_list(byte_list):
        return list(map(lambda x: x.decode("utf-8"), byte_list))


class Emotion:
    @staticmethod
    def feel(sentiment):
        print('Feeling sentiment')
        if sentiment.polarity < -0.7:
            return 'curse'


class Memory:
    REDIS_DB = {"words": 0, "reactions": 1, "ignored words": 2, "new words": 3}
    new_words = []
    redis_connections = {}

    def __init__(self):
        for name, db in self.REDIS_DB.items():
            self.redis_connections[name] = redis.StrictRedis(host='localhost', port=6379, db=db)

    def init_memory(self, name):
        return self.redis_connections[name]

    def search_word(self, words):
        memory = self.redis_connections['words']
        print('Searching for a match among a list of words: ' + ', '.join(words))
        for word in words:
            intent = memory.get(word)
            if intent:
                print("Found an intent in memory")
                return intent.decode("utf-8")
        self.new_words += words
        self.remember_new_words()

    def remember_new_words(self):
        memory = self.redis_connections['new words']
        for word in self.new_words:
            memory.incr(word)

    def filter_ignored_words(self, words):
        filtered = []
        memory = self.redis_connections['ignored words']
        for word in words:
            ignore = memory.get(word)
            if ignore is None:
                filtered.append(word)
        return filtered

    def forget(self, words, memory_type):
        if not words:
            return
        print("Deleting these words from short term memory: " + ", ".join(words))
        memory = self.redis_connections[memory_type]
        words_tuple = tuple(words)
        memory.delete(*words_tuple)

    def ignore(self, words):
        if not words:
            return
        print("Adding these words to ignore memory: " + ", ".join(words))
        memory = self.redis_connections['ignored words']
        for word in words:
            memory.set(word, "useless")

    def list_all(self, memory_type):
        memory = self.redis_connections[memory_type]
        return Utils.byte_string_list(memory.keys())

    def add_words(self, words, memory_type, value):
        memory = self.redis_connections[memory_type]
        for word in words:
            memory.set(word, value)


class Motor:
    ROUTINES = {"did you learn": "common_words", "please forget ": "forget_words", "please ignore ": "ignore_words",
                "list all ": "show_memory", "please add ": "memorize_word"}
    memory = Memory()
    emotion = Emotion()

    def react(self, intent):
        print("Reacting to intent " + intent)
        memory = self.memory.redis_connections['reactions']
        responses = memory.lrange(intent, 0, -1)
        return random.choice(responses).decode("utf-8")

    def check_word(self, word):
        print("Checking word " + word)
        intent = self.memory.search_word([word])
        if intent is None:
            words = external.research(word, self.memory)
            intent = self.memory.search_word(words)
        if intent:
            return self.react(intent)

    def check_tone(self, sentiment):
        print("Checking tone")
        reaction = Emotion.feel(sentiment)
        if reaction:
            return self.react(reaction)


class Routine:
    def __init__(self, motor):
        self.motor = motor

    def execute(self, routine_name, text):
        routine = getattr(self, routine_name)
        return routine(text)

    def common_words(self, text):
        frequency = {}
        memory = self.motor.memory.redis_connections['new words']
        words = memory.keys()
        for word in words:
            frequency[word] = memory.get(word)
        sorted_words = sorted(frequency.items(), key=operator.itemgetter(1), reverse=True)
        common_words = Utils.byte_string_list([x[0] for x in sorted_words[:25]])
        return "Here's a list of the most common words I learned: " + ', '.join(common_words)

    def forget_words(self, text):
        words = text.split("forget ", 1)[1].split(', ')
        self.motor.memory.forget(words, 'new words')
        return "I forgot these words: " + ', '.join(words)

    def ignore_words(self, text):
        words = text.split("ignore ", 1)[1].split(', ')
        self.motor.memory.ignore(words)
        self.motor.memory.forget(words, 'new words')
        return "I'm now ignoring these words: " + ', '.join(words)

    def show_memory(self, text):
        memory_type = text.split("list all ", 1)[1]
        memories = self.motor.memory.list_all(memory_type)
        return "Here's a list of the " + memory_type + " I know: " + ', '.join(memories)

    def memorize_word(self, text):
        command = text.split("please add ", 1)[1]
        split = command.split(" to ", 1)
        words = split[0].split(', ')
        reaction = TextBlob(split[1]).words[0]
        self.motor.memory.add_words(words, 'words', reaction)
        return "I just associated word(s) " + ', '.join(words) + ' to my reaction "' + reaction + '".'


class Hearing:
    @staticmethod
    def get_words(sentence, memory):
        words = []
        text_blob = TextBlob(sentence)
        for word, pos in text_blob.tags:
            if pos[:2] in ['NN', 'VB', 'JJ']:
                words.append(word)
        filtered_words = memory.filter_ignored_words(filter(lambda item: item, words))
        return filtered_words

    def get_raw_words(self, sentences, memory):
        words = []
        for sentence in sentences:
            words += self.get_words(sentence, memory)
        return words

    @staticmethod
    def get_sentiment(sentence):
        text_blob = TextBlob(sentence)
        return text_blob.sentiment
