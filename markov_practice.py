import numpy as np
from tqdm import tqdm
import tables
from scipy.sparse import csr_matrix
import random
import re

global fileName
fileName = 'matrix.h5'

def clean_websters():
    # cleaning up dictionary text file
    with open('websters_1913_short.txt', 'r') as f1:
        d = False

        defn = []
        dictionary = []

        for row in f1:
            line = row.split()

            if line:
                if line[0] == 'Defn:':
                    line.pop(0)
                    d = True

            if not line and d == True:
                d = False
                for index, element in enumerate(defn):
                    if defn[index] == '[Obs.]':
                        defn = defn[:index]
                        break

                # adding each definitions to a list
                dictionary.append(defn[:])
                del defn[:]

            if d == True: defn += line
    return dictionary

def create_index_of_words(word_list):
    all_words = {}
    column = 0

    print "building word list"
    for row in tqdm(word_list):
        for word in row:
            if word not in all_words:
                all_words[word] = column
                column += 1

    all_words['start_of_sentence'] = column
    all_words['end_of_sentence'] = column+1

    return all_words

def populate_matrix(word_index, word_list):

    n = len(word_index)

    m = csr_matrix((n,n), dtype=np.float32).toarray()

    print "populating sparse matrix"
    for i_row, row in enumerate(tqdm(word_list)):

        for i_word, word in enumerate(row):

            if i_word == 0:
                current = word_index['start_of_sentence']
                after = word_index[word]
                m[current, after] += 1

            try:
                current = word_index[word]
                after = word_index[row[i_word+1]]
            except IndexError:
                after = word_index['end_of_sentence']

            m[current, after] += 1

    nz_elements = []

    print "normalizing sparse matrix"
    for key in tqdm(word_index):

        total = sum(m[word_index[key],:])
        total = 1

        if total == 0: continue

        nz_elements = np.nonzero(m[word_index[key],:])

        for element in nz_elements:
            m[word_index[key],element] /= total

    return m

def response(word_index, t_matrix):

    choice = 0
    m, n = t_matrix.shape

    while True:
        index = random.randint(0, n-1)
        choice = t_matrix[word_index['start_of_sentence'],index]

        if choice > random.random():
            next_word = index
            for word, col in word_index.iteritems():
                if col == index:
                    output = word
            break

    choice = 0

    while True:
        current_word = next_word

        index = random.randint(0, n-1)
        choice = t_matrix[current_word,index]

        if choice > random.random():
            next_word = index
            if next_word == word_index['end_of_sentence']:
                return output
            for word, col in word_index.iteritems():
                if col == index:
                    output += " %s" % word

    return


def main():

    number = 10

    dictionary = clean_websters()

    all_words = create_index_of_words(dictionary)

    weight_matrix = populate_matrix(all_words, dictionary)

    for i in range(number):
        definition = response(all_words, weight_matrix)
        print "definition: %s" % definition

    return

main()
