import pyaudio
import speech_recognition as sr
import sys
import pandas as pd
import re

from transformers import pipeline

is_adding_symptoms = True
list_symptoms = []

# Import data
df = pd.read_csv("data/maladies_et_symptomes.csv")
df.head()

df.drop(["Unnamed: 0","0","3","5","7","9"],inplace=True,axis=1)

def clean_symptoms_col_2(text):
    resultat = re.sub("^\[\{\"symptoms\":\"", "", text)
    resultat = re.sub("\"}", "", resultat)
    return resultat

def clean_symptoms(text):
    resultat = re.sub("^\{\"symptoms\":\"", "", text)
    resultat = re.sub("\"}", "", resultat)
    return resultat

df["2"] = df["2"].map(clean_symptoms_col_2)
df["4"] = df["4"].map(clean_symptoms)
df["6"] = df["6"].map(clean_symptoms)
df["8"] = df["8"].map(clean_symptoms)

df['symptoms'] = df["2"] + " " + df["4"] + " " + df["6"] + " " + df["8"]

df.drop(["2","4","6","8"],inplace=True,axis=1)

df["symptoms"] = df["symptoms"].str.lower()

def speak_into_microphone(question,language="en-US"):
    # Prise de la voix
    r = sr.Recognizer()
    print("--------------------------------------")
    print(question)
    print("--------------------------------------")
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language=language)
        print("--------------------------------------")
        print("J'ai entendu :", text)
        print("--------------------------------------")
    except sr.UnknownValueError:
        print("--------------------------")
        print("J'ai rien compris")
        print("--------------------------")
    except sr.RequestError as e:
        print("--------------------------")
        print("L'API Speech de Google est hors service" + format(e))
        print("--------------------------")

    return text

# Choix de l'utilisateur
text = speak_into_microphone("What is your language (say 'french' or 'spain') ?")

if text == "French":
    language = "fr-FR"
    pipeline_name = "translation_fr_to_en"
    model_name = "Helsinki-NLP/opus-mt-fr-en"
    question = "Quels sont vos symptômes ?"
    repeat_question = "Voulez-vous rajouter un symptôme ?"
    positive_answer = "oui"
    negative_answer = "non"
    
else:
    language = "es-ES"
    model_name = "Helsinki-NLP/opus-mt-es-en"
    question = "Cuales son sus sintomas ?"
    pipeline_name = "translation_es_to_en"
    repeat_question = ""
    positive_answer = "si"
    negative_answer = "no"


def traduction(input):
    translator = pipeline(pipeline_name, model=model_name)
    lang_origin = translator(input)
    output = lang_origin[0]['translation_text']

    print("\nLangue d'origine:")
    print(input)
    print('\nEnglish:')
    print(lang_origin[0]['translation_text'])

    return output


text = speak_into_microphone(question,language)
list_symptoms.append(text)
print("--------------------------")
print(list_symptoms)
print("--------------------------")

while is_adding_symptoms:

    print("--------------------------")
    choice = speak_into_microphone(repeat_question + " " + positive_answer + " ?" + " " + negative_answer + " ?",language)
    print("--------------------------")

    if choice == positive_answer:

        text = speak_into_microphone(repeat_question,language)

        list_symptoms.append(text)
        print("--------------------------")
        print(list_symptoms)
        print("--------------------------")

    else:
        is_adding_symptoms = False


print("--------------------------")
print("The doctor's answer will arrive in a few moments... The cost of the consultation is 100 euros. Thank you for waiting")
print("--------------------------")

trad = traduction(" ".join(list_symptoms))

print("Your disease is :")
print(df[df['symptoms'].str.contains(trad)])
    