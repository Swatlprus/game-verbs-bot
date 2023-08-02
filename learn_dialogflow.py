import json
from environs import Env
from google.cloud import dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Create an intent of the given intent type."""

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )
    return response


if __name__ == '__main__':
    env = Env()
    env.read_env()
    project_id = env('PROJECT_ID')
    path_questions = env('PATH_QUESTIONS', 'questions.json')

    with open(path_questions, "r") as questions_file:
        questions_json = questions_file.read()
    questions = json.loads(questions_json)

    for intent in questions.keys():
        training_phrases_parts = questions[intent]['questions']
        message_texts = questions[intent]['answer']
        create_intent(
            project_id,
            intent,
            training_phrases_parts,
            [message_texts],
        )
