import json
import requests

dev_url = 'http://172.31.138.15:5323/kbqa'

# question = '60后的官员有哪些'
while True:
    database = requests.get('http://172.31.98.16:7405/schemaread/neo4jinfo/')
    database = json.loads(database.text)
    url = database['api']['bolt']
    password = database['password']
    print(url, password)
    # print(database)
    # print(json.loads(database.text))
    question = input('question:')
    question_dict = {'question': question}
    try:
        r = requests.post(dev_url, json=question_dict)
        print(r)
        print('intent', r.json()['intent'])
        print('answer', r.json()['string'])
    except:
        print([])
        print([])
    print('----------------------------------------------------------------')
