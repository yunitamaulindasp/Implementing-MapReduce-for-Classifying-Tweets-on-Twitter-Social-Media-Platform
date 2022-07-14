# Program_Klasifikasi.py

import PySimpleGUI as sg
import re
import string
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import pandas as pd
import numpy as np
import time
import gif

def cleantxt(text):
    text = re.sub("b'+", '', text)
    text = re.sub('@[A-Za-z0-9_]+', '', text)
    text = re.sub('#[A-Za-z0-9_]+', '', text)
    text = re.sub('RT[\s]+', '', text)
    text = re.sub(r"http\S+", "", text)
    return text


def proses_text(isi):

    isi = cleantxt(isi)
    isi = isi.lower()
    isi = re.sub(r"\d+", "", isi)

    factory = StopWordRemoverFactory()
    more_stopword = ['t', 'r', 'n', 'xc2', 'xb0', 'xe2', 'x97', 'xa1', 'xc2', 'xb0', 'x0c', 'x0b']
    datab = factory.get_stop_words() + more_stopword
    stopword = factory.create_stop_word_remover()
    isi = stopword.remove(isi)

    isi = isi.translate(str.maketrans("", "", string.punctuation))

    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    isi = stemmer.stem(isi)

    isi = isi.split()

    normalizad_word = pd.read_excel("kamus/slangword.xlsx")

    normalizad_word_dict = {}

    for index, row in normalizad_word.iterrows():
        if row[0] not in normalizad_word_dict:
            normalizad_word_dict[row[0]] = row[1]

    def normalized_term(text):
        return [normalizad_word_dict[term] if term in normalizad_word_dict else term for term in text]

    isi = normalized_term(isi)

    return isi


def bobot_tweet(tweet):
    positif_file = open("kamus/positive.txt").read()
    positif_word = positif_file.split('\n')
    negatif_file = open("kamus/negative.txt").read()
    negatif_word = negatif_file.split('\n')

    jml = 0

    for kata in tweet:
        if kata in positif_word:
            jml = jml + 1
        elif kata in negatif_word:
            jml = jml - 1

    return jml


def kelompok_tweet(bobot):
    if bobot < 0:
        kelompok = "Negatif"
    elif bobot >= 0:
        kelompok = "Positif"

    return kelompok

mapper = []
def map(data):
    i = 0
    for kalimat in data['tweet']:
        line = kalimat.strip()
        preprocessing = proses_text(line)
        bobot_kalimat = bobot_tweet(preprocessing)
        hasil = kelompok_tweet(bobot_kalimat)

        if hasil == "Positif":
            window['-FILE POSITIF-'].print(kalimat)
        elif hasil == "Negatif":
            window['-FILE NEGATIF-'].print(kalimat)

        words = hasil.split()

        i = i + 1

        for word in words:
            mapper.append('%s %s' % (word, "1"))

        window1['progresbar'].update_bar(i)

reducer = []
def reduce(data):
    current_word = None
    current_count = 0
    word = None

    for line in data:
        line = line.strip()

        word, count = line.split(' ', 1)

        try:
            count = int(count)
        except ValueError:
            continue

        if current_word == word:
            current_count += count
        else:
            if current_word:
                window['-FILE HASIL-'].print('%s %s' % (current_word, current_count))
            current_count = count
            current_word = word

    if current_word == word:
        window['-FILE HASIL-'].print('%s %s' % (current_word, current_count))


file_column = [
    [
        sg.Text("File Tweet"),
        sg.In(size=(61,1), enable_events=True, key="-TWEET-"),
        sg.FileBrowse(file_types=(("Tweet Files", "*.csv"),)),
        sg.Button("Proses"),
    ],
]

positif_column = [
    [
        sg.Text("Daftar Tweet Positif"),
    ],
    [
        sg.Multiline(
            size=(40, 20),
            key="-FILE POSITIF-",
            disabled=True,
        )
    ],
]

negatif_column = [
    [
        sg.Text("Daftar Tweet Negatif"),
    ],
    [
        sg.Multiline(
            size=(40, 20),
            key="-FILE NEGATIF-",
            disabled=True,
        )
    ],
]

texthasil = [
    [
        sg.Text("Hasil Pemrosesan"),
    ],
]

mulailagi = sg.Column(
    [[sg.Button("Reset", size=(10,1))]],
    element_justification="right",
    vertical_alignment="button",
    expand_x=True,
)

hasil_column = [
    [
        sg.Multiline(
            size=(87, 10),
            key="-FILE HASIL-",
            disabled=True,
        )
    ],
]

layout = [
    [
        sg.Column(file_column),
    ],
    [
        sg.Column(positif_column),
        sg.VSeperator(),
        sg.Column(negatif_column),
    ],
    [
        sg.Column(texthasil),
        mulailagi
    ],
    [
        sg.Column(hasil_column),
    ],
] 

layout1 = [
    [sg.ProgressBar(100,orientation='h', size=(20,20), border_width=4, key='progresbar', bar_color=['green','gray'])]
]

window = sg.Window("Program Klasifikasi Tweet 2.0", layout)
window1 = sg.Window("Tunggu Sebentar", layout1)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    elif event == "Proses":
        data = pd.read_csv(values['-TWEET-'])
        banyak = int(data['tweet'].count())
        event, values = window1.Read(timeout=100)
        window1['progresbar'].update(current_count = 0, max = banyak)
        start_time = time.time()
        map(data)
        maper = np.array(mapper)
        maper.sort()
        reduce(maper)
        window1.close()
        window['-FILE HASIL-'].print('Lama Pemrosesan %s seconds' % (time.time() - start_time))
    elif event == "Reset":
        window['-TWEET-']('')
        window['-FILE POSITIF-'].update('')
        window['-FILE NEGATIF-'].update('')
        window['-FILE HASIL-'].update('')
        break
