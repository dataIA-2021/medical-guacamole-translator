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
        print("I heard :", text)
        print("--------------------------------------")
    except sr.UnknownValueError:
        print("--------------------------")
        print("I don't understand")
        print("--------------------------")
    except sr.RequestError as e:
        print("--------------------------")
        print("L'API Speech de Google est hors service" + format(e))
        print("--------------------------")

    return text

# Choix de l'utilisateur
print("--------------------------------------")
print("Hello, I am Sofia, your personal medical assistant")
text = speak_into_microphone("What is your language (say 'french' or 'spain') ?")

if text == "French":
    language = "fr-FR"
    pipeline_name = "translation_fr_to_en"
    model_name = "Helsinki-NLP/opus-mt-fr-en"
    question = "Quels sont vos sympt??mes ?"
    repeat_question = "Voulez-vous rajouter un sympt??me ?"
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

    print("\ntranslate in progress...")
    translator = pipeline(pipeline_name, model=model_name)
    lst_trad = []

    for symptom in input:

        lang_origin = translator(symptom)
        output = lang_origin[0]['translation_text']
        print("\nLangue d'origine:")
        print(input)
        print('\nEnglish:')
        lst_trad.append(lang_origin[0]['translation_text'])
        print(lst_trad)
    
    return lst_trad


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

# Paiement
print("--------------------------")
print("The doctor's answer will arrive in a few moments... The cost of the consultation is 100 euros. Thank you for waiting")
print("--------------------------")
print("--------------------------")
print("PLEASE, DON'T FORGET TO INSERT YOUR CREDIT CARD ! Thank you for choosing our service :) (You can also pay with kebabcoin, contact support IT Victorien for this)")
print("--------------------------")

def search(list):

    print("--------------------------")
    print("Your diseases could be :")
    diseases = []

    symptom = list[0].lower()
    diseases_found = df["1"][df["symptoms"].str.contains(symptom) == True].tolist()

    # Ajout des maladies dans la liste
    for disease_found in diseases_found:
        if disease_found not in diseases:
            diseases.append(disease_found)

    i=1
    for i in range(len(list)):
        symptom = list[i].lower()
        diseases_found = df["1"][df["symptoms"].str.contains(symptom) == True].tolist()

        # alcoolic
        new_diseases = []
        for disease_found in diseases_found:
            if disease_found in diseases:
                new_diseases.append(disease_found)

        diseases = new_diseases

    return diseases


print(search(traduction(list_symptoms)))
print("--------------------------")
