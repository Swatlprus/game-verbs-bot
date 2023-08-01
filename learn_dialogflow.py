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

    print("Intent created: {}".format(response))


def open_file(base_questions):
    with open(base_questions, "r") as questions_file:
        questions_json = questions_file.read()

    questions = json.loads(questions_json)
    training_phrases_parts = questions['Устройство на работу']['questions']
    message_texts = questions['Устройство на работу']['answer']
    return training_phrases_parts, message_texts


if __name__ == '__main__':
    env = Env()
    env.read_env()
    project_id = env('PROJECT_ID')
    base_questions = env('BASE_QUESTIONS', 'questions.json')
    training_phrases_parts, message_texts = open_file(base_questions)
    create_intent(
        project_id,
        'Как устроиться к вам на работу',
        training_phrases_parts,
        [message_texts],
    )
