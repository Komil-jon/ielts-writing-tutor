from g4f.client import Client
import time
import json
import requests
from flask import Flask, request
import os
from pymongo import MongoClient
#global last_update_id
# used only for testing 👆


BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN = os.getenv('ADMIN')
GROUP = os.getenv('GROUP')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        process(json.loads(request.get_data()))
        return 'Success!'
    except Exception as e:
        print(e)
        return 'Error'

def testing():
    global last_update_id
    last_update_id = -1
    while True:
        updates = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id}").json().get('result', [])
        for update in updates:
            process(update)
            last_update_id = update['update_id'] + 1


def process(update):
    if 'message' in update:
        if 'text' in update['message']:
            message = update['message']['text']
            if message == '/start':
                if database_search(update['message']['from']['id']) == None:
                    record = {
                        "id": update['message']['from']['id'],
                        "name": update['message']['from']['first_name'],
                        "username": update['message']['from'].get('username', 'None')
                    }
                    database_insert(record)
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',params={'chat_id': update['message']['from']['id'],'text': f"✅ Hello <a href='tg://user?id={update['message']['from']['id']}'>{update['message']['from']['first_name']}</a> !",'parse_mode': 'HTML'})
                    alert(update['message']['from'])
                with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                    file.write(' ')
                menu(update['message']['from']['id'], '_Welcome!_')
            elif message == 'Task 1':
                with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                    file.write(' ')
                data = {'chat_id': update['message']['from']['id'],'text': f"_Currently we are working to add this function_", 'parse_mode': 'Markdown'}
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)
            elif message == 'Task 2':
                with open(f"{update['message']['from']['id']}.txt", 'w') as file:
                    file.write('2 N')
                data = {'chat_id': update['message']['from']['id'], 'text': f"_Now send your essay topic_",'parse_mode': 'Markdown'}
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)
            elif message == '/menu':
                menu(update['message']['from']['id'], '_Choose!_')
            else:
                try:
                    with open(f"{update['message']['from']['id']}.txt", 'r') as file:
                        model = file.readline()
                    if model == ' ':
                        menu(update['message']['from']['id'], '_Choose!_')
                    elif len(model) == 1 or len(model) == 3:
                        send_topic(update['message']['from']['id'], update['message']['text'])
                    else:
                        initial(update['message']['from']['id'], update['message']['text'], model[0], model[2:])
                except:
                    data = {'chat_id': update['message']['from']['id'],'text': f"_System has been updated! please re /start_", 'parse_mode': 'Markdown'}
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)

def send_topic(user_id, topic):
    with open(f"{user_id}.txt", 'r') as file:
        mode = file.readline()[0]
    with open(f"{user_id}.txt", 'w') as file:
        file.write(f"{mode} {topic}")
    data = {'chat_id': user_id, 'text': f"_Now send your essay_", 'parse_mode': 'Markdown'}
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)
    return


def initial(user_id, query, mode, topic):
    if mode == '1':
        instruction = os.getenv('TASK_ONE')
    else:
        instruction =instruction = os.getenv('TASK_TWO')
    client = Client()
    response = client.chat.completions.create(
        provider='',  # Replace with your provider
        model="blackbox",
        messages=[{'role': 'user', 'content': instruction + topic + "\n\nHere is my essay itself\n\n" + query}],
        stream=True)
    evaluate(response, user_id, mode)
    with open(f"{user_id}.txt", 'w') as file:
        file.write(' ')
    return

def database_search(id):
    connection_string = f"mongodb+srv://{USERNAME}:{PASSWORD}@core.pur20xh.mongodb.net/?appName=Core"
    client = MongoClient(connection_string)
    db = client['writing_check']
    collection = db['users']
    return collection.find_one({"id": id})

def database_insert(record):
    connection_string = f"mongodb+srv://{USERNAME}:{PASSWORD}@core.pur20xh.mongodb.net/?appName=Core"
    client = MongoClient(connection_string)
    db = client['writing_check']
    collection = db['users']
    collection.insert_one(record)

def evaluate(response, user_id, mode):
    output = ""
    edit_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
        json={'chat_id': user_id, 'text': f'✅ _Your Task {mode} is being checked..._','parse_mode': 'Markdown'}).json()['result']['message_id']

    last_print_time = time.time()
    for chunk in response:
        if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
            # Append the chunk to the collected response
            for choice in chunk.choices:
                if hasattr(choice, 'delta') and choice.delta is not None and hasattr(choice.delta, 'content'):
                    content = choice.delta.content
                    if content is not None:
                        output += content

        # Print the collected response every 2 seconds
        current_time = time.time()
        if current_time - last_print_time >= 2:
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': f'{output}', 'message_id': edit_id, 'parse_mode': 'Markdown'}).json()
            last_print_time = current_time
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',json={'chat_id': user_id, 'text': output, 'message_id': edit_id, 'parse_mode': 'Markdown'})


def menu(user_id, text):
    keyboard = {'keyboard': [['Task 1', 'Task 2']], 'one_time_keyboard': False, 'resize_keyboard': True}
    data = {'chat_id': user_id, 'text': text, 'reply_markup': json.dumps(keyboard), 'parse_mode': 'Markdown'}
    print(requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data).json())
    return

def alert(user):
    params = {'chat_id': ADMIN, 'text': "<strong>NEW MEMBER!!!\n</strong>" + json.dumps(user), 'parse_mode': 'HTML', }
    print(requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params=params))

if __name__ == '__main__':
    app.run(debug=False)
    #testing()
