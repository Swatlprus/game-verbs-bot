import json
from environs import Env


env = Env()
env.read_env()
base_questions = env('BASE_QUESTIONS', 'questions.json')

with open(base_questions, "r") as questions_file:
    questions_json = questions_file.read()
questions = json.loads(questions_json)

for item in questions.keys():
    training_phrases_parts = questions[item]['questions']
    message_texts = questions[item]['answer']
    print('START')
    print(item)
    print(training_phrases_parts)
    print(message_texts)
    print('END')
