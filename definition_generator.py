import random
import numpy as np
from tqdm import tqdm
from scipy.sparse import csr_matrix

# Ignore divide by 0 in matrix probability calc
np.seterr(divide='ignore', invalid='ignore')

def clean_text(fname = 'websters_1913_short.txt'):
    '''Clean dictionary text file

    Input:

    Text file version of dictionary. Definitions start with 'Defn:'

    Output:

    List of lists. Each inner list is a definition.
    '''

    with open(fname, 'r', encoding='latin-1') as f:

        list_of_defs = []

        while True:
            row = f.readline()
            if not row: break

            if 'Defn:' in row:

                # Read in first line of definition
                definition = row.split()[1:]

                # Add subsequent lines of definition
                while row and row != '\n':
                    row = f.readline()
                    definition += row.split()

                # Add definition to list of defintions
                list_of_defs.append(definition)

    return list_of_defs

def create_index_of_words(list_of_defs):
    '''Create dict for index of words

    Input:

    List of lists. Each inner list contains one word per element.

    Output:

    Dict with each key is a word and each value is a row and column number
    '''

    # Create dict and index variable
    unique_words = {}
    index = 0

    for row in tqdm(list_of_defs):
        for word in row:
            if word not in unique_words:
                unique_words[word] = index
                index += 1

    unique_words['start_of_definition'] = index
    unique_words['end_of_definition'] = index + 1

    return unique_words


def populate_matrix(unique_words, list_of_defs):

    n = len(unique_words)

    # Form empty transition matrix
    t_matrix = csr_matrix((n,n), dtype=np.float32).toarray()

    # Populate sparse matrix with number of transitions
    for i_row, row in enumerate(tqdm(list_of_defs)):

        current = unique_words['start_of_definition']

        try:
            after = unique_words[row[0]]
        except IndexError: continue

        t_matrix[current, after] += 1

        for i_word, word in enumerate(row):

            current = unique_words[word]

            try:
                after = unique_words[row[i_word+1]]
            except IndexError:
                after = unique_words['end_of_definition']

            t_matrix[current, after] += 1

    return t_matrix

def get_transition_probability(key, t_matrix, unique_words):

    # Convert transition matrix to probability matrix

    column_sum = t_matrix[unique_words[key],:].sum()

    prob_array = t_matrix[unique_words[key],:] / column_sum

    return prob_array

def get_next_word(current_word, t_matrix, unique_words):

    prob_array = get_transition_probability(current_word, t_matrix, unique_words)

    # Randomly select one of the nonzero elements
    nonzero_probs = np.nonzero(prob_array)

    while True:
        choice = random.choice(nonzero_probs[0])

        choice_prob = prob_array[choice]
        random_prob = random.random()

        if choice_prob > random_prob:
            print('Chosen: %s < %s (%s)' % (random_prob, choice_prob, choice))

            for key, value in unique_words.items():
                if value == choice:

                    print('Word chosen: %s' % key)

                    next_word = key

                    return next_word
        """
        else:
            print('NOT chosen: %s > %s (%s)' % (random_prob, choice_prob, choice))
        """


def main():

    # Generate a list of definitions from a text file of Websters dictionary
    list_of_defs = clean_text('websters_1913.txt')

    # Create index of unique words found in definitions
    unique_words = create_index_of_words(list_of_defs)

    # Generate transition matrix based on the definitions found in the dictionary
    t_matrix = populate_matrix(unique_words, list_of_defs)

    current_word = 'start_of_definition'

    output_def = 'Definition = '

    while True:
        next_word = get_next_word(current_word, t_matrix, unique_words)

        if next_word == 'end_of_definition':
            print(output_def)
            return

        else:
            output_def += next_word + ' '
            current_word = next_word

main()
