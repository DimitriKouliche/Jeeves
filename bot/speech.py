from bot import brain


def respond(motor, input_text):
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
    important_words = brain.Hearing.get_words(input_text, motor.memory)
    for word in important_words:
        word_match = motor.check_word(word)
        if word_match:
            return word_match


def search_routine(motor, input_text):
    for sentence, routine_name in motor.ROUTINES.items():
        if sentence in input_text:
            routine = brain.Routine(motor)
            return routine.execute(routine_name, input_text)
