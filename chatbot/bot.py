import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import pickle
import tflearn
import nltk
# nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import random
import json


with open("chatbot//bot_files//intents.json", encoding='utf-8') as file:
    data = json.load(file)

with open("chatbot//bot_files//data.pkl", "rb") as f:
    words, labels, training, output = pickle.load(f)

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation = "softmax")
net = tflearn.regression(net)
model = tflearn.DNN(net)

model.load("chatbot//bot_files//model.tflearn")

def bag_of_words(s, words):
    stemmer = LancasterStemmer()
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(w) for w in s_words]

    for se in s_words:
        for i,w in enumerate(words):
            if w == se:
                bag[i] = 1
    bag = np.array(bag)
    bag = np.reshape(bag,[-1,len(bag)])
    return bag

def api(message:str):
    message = message.lower()
    results = model.predict(bag_of_words(message, words))
    index = np.argmax(results)
    tag = labels[index]
    if results[0][index] > 0:
        for tg in data['intents']:
            if tg['tag'] == tag:
                responses = tg['responses']
        return random.choice(responses)
    else:
        return "Sorry I am unable to understand this."
