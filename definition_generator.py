import numpy as np
from tqdm import tqdm
from scipy.sparse import csr_matrix

# Ignore divide by 0 in matrix probability calc
np.seterr(divide='ignore', invalid='ignore')

def clean_text(fname = 'websters_1913_short.txt'):
    """Clean dictionary text file

    Input:

    Text file version of dictionary. Definitions start with "Defn:"

    Output:

    List of lists. Each inner list is a definition.
    """

    with open(fname, 'r') as f:

        list_of_defs = []

        while True:
            row = f.readline()
            if not row: break

            if 'Defn:' in row:

                # Read in first line of definition
                definition = row.split()[1:]

                # Add subsequent lines of definition
                while row and row != "\n":
                    row = f.readline()
                    definition += row.split()

                # Add definition to list of defintions
                list_of_defs.append(definition)

    return list_of_defs

def create_index_of_words(list_of_defs):
    """Create dict for index of words

    Input:

    List of lists. Each inner list contains one word per element.

    Output:

    Dict with each key is a word and each value is a row and column number
    """

    # Create dict and index variable
    word_dict = {}
    index = 0

    for row in tqdm(list_of_defs):
        for word in row:
            if word not in word_dict:
                word_dict[word] = index
                index += 1

    word_dict['start_of_sentence'] = index
    word_dict['end_of_sentence'] = index + 1

    return word_dict


def populate_matrix(word_dict, list_of_defs):

    n = len(word_dict)

    # Form empty transition matrix
    trans_mat = csr_matrix((n,n), dtype=np.float16).toarray()

    # Populate sparse matrix with number of transitions
    for i_row, row in enumerate(tqdm(list_of_defs)):

        current = word_dict['start_of_sentence']

        try:
            after = word_dict[row[0]]
        except IndexError: continue

        trans_mat[current, after] += 1

        for i_word, word in enumerate(row):

            current = word_dict[word]

            try:
                after = word_dict[row[i_word+1]]
            except IndexError:
                after = word_dict['end_of_sentence']

            trans_mat[current, after] += 1

    # Convert transition matrix to probability matrix
    for key in tqdm(word_dict):

        total = sum(trans_mat[word_dict[key],:])

        if total == 0:
            continue

    prob_mat = trans_mat / trans_mat.sum(axis=0).T
    print(prob_mat)

    return prob_mat


def response(word_dict, t_matrix):

    choice = 0
    m, n = t_matrix.shape

    while True:
        index = random.randint(0, n-1)
        choice = t_matrix[word_dict['start_of_sentence'],index]

        if choice > random.random():
            next_word = index
            for word, col in word_dict.iteritems():
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
            if next_word == word_dict['end_of_sentence']:
                return output
            for word, col in word_dict.iteritems():
                if col == index:
                    output += " %s" % word

    return


def main():

    list_of_defs = clean_text('websters_1913.txt')
    # list_of_defs = clean_text()

    word_dict = create_index_of_words(list_of_defs)

    prob_mat = populate_matrix(word_dict, list_of_defs)

    print(type(prob_mat))
    print(prob_mat.size)
    print(prob_mat.shape)

    return

"""

    for i in range(number):
        definition = response(word_dict, weight_matrix)
        print "definition: %s" % definition

"""
main()
