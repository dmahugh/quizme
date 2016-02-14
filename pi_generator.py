"""Generate a quizme JSON file for the first 100 digits of pi.

Generates 20 questions, each one asking for a missing 5-digit series from
the first 100 digits of Pi. Order of the questions and answers is random.
"""
import json
import random


def random5digits():
    """Generate a random 5-digit string of numbers.
    """
    return (str(random.randint(0, 9)) + str(random.randint(0, 9)) +
            str(random.randint(0, 9)) + str(random.randint(0, 9)) +
            str(random.randint(0, 9)))


FILENAME = "data\Pi.json"
PI = ('3.14159265358979323846264338327950288419716939937510'
      '58209749445923078164062862089986280348253421170679')

chunks = list(range(0, 20)) # pylint: disable=C0103
random.shuffle(chunks)

questions = {} # pylint: disable=C0103

for nchunk in range(0, 20):

    offset = 5*chunks[nchunk] + 2

    answer = PI[offset:offset+5]
    question = PI[0:offset] + 'xxxxx' + PI[offset+5:]
    answerno = random.randint(1, 5)

    answers = {}
    for nanswer in range(1, 6):
        answers[str(nanswer)] = \
             answer if nanswer == answerno else random5digits()

    q_json = {str(nchunk+1): \
        {"question": question, "answers": answers, "correct": str(answerno), \
        "explanation": 'PI = '+PI, "image": "pi.png"}}

    questions.update(q_json) # add this question to the master dictionary

# write the file
with open(FILENAME, 'w') as jsonfile:
    json.dump(questions, jsonfile)
