import random
import numpy as np
from tqdm import tqdm
from scipy.sparse import csr_matrix

# Ignore divide by 0 in matrix probability calc
np.seterr(divide='ignore', invalid='ignore')

def clean_text(fname = 'websters_1913.txt'):
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

    print("%s definitions found in %s" % (len(list_of_defs), fname))

    return list_of_defs


class def_gen():

    def __init__(self, list_of_defs):
        """Instantiate dictionary of unique words and list of definitions"""
        self.unique_words = {}
        self.list_of_defs = list_of_defs

    def create_index_of_words(self):
        """Create dict of unique words in dictionary definitions."""

        # Start index at 0
        index = 0

        print("Building dict of unique words...")
        for row in tqdm(self.list_of_defs):
            for word in row:
                if word not in self.unique_words:
                    # Assign each unique word an index
                    self.unique_words[word] = index
                    index += 1

        # Transitions from start and to end of definitions needed
        self.unique_words['start_of_definition'] = index
        self.unique_words['end_of_definition'] = index + 1


    def create_trans_matrix(self):
        """Create matrix of number of transitions from one word to another."""

        # Create empty sparse transition matrix
        n = len(self.unique_words)
        self.t_matrix = csr_matrix((n,n), dtype=np.float32).toarray()

        print("Populating sparse transition matrix...")
        for i_row, row in enumerate(tqdm(self.list_of_defs)):

            # First transition is from 'start_of_definition' to first element
            current_word = self.unique_words['start_of_definition']

            try: next_word = self.unique_words[row[0]]
            except IndexError: continue

            self.t_matrix[current_word, next_word] += 1

            # Loop through each definition
            for i_word, word in enumerate(row):
                current_word = self.unique_words[word]

                try:
                    next_word = self.unique_words[row[i_word+1]]
                except IndexError:
                    next_word = self.unique_words['end_of_definition']

                # Add one to the right cell for each transition
                self.t_matrix[current_word, next_word] += 1

    def get_transition_probability(self, word):
        """ Convert specified row contents from number of transitions to
        next word to probability of transition to the next word.

        Input:

        String specifying which row is to be used.

        Output:

        Numpy array with probabilities of transitioning to the next word.
        Elements of array are floats between 0.0 and 1.0.
        """

        # Convert transition matrix to probability matrix
        row_sum = self.t_matrix[self.unique_words[word],:].sum()
        prob_array = self.t_matrix[self.unique_words[word],:] / row_sum

        return prob_array

    def get_next_word(self, current_word):
        """ Take one word and choose the next word using the probabilities
        in the transition matrix.

        Input:

        String specifying which word is the current word.

        Output:

        String specifying which word is the next word.
        """

        # Create array of indices with nonzero transition probability
        prob_array = self.get_transition_probability(current_word)
        nonzero_probs = np.nonzero(prob_array)

        iterations = 0

        while True:
            # Randomly select one of the nonzero elements
            choice = random.choice(nonzero_probs[0])

            choice_prob = prob_array[choice]
            random_prob = random.random()

            # Keep track of how many tries it takes
            iterations += 1

            # Next word is only selected if prob is greater than random prob
            if choice_prob > random_prob:
                for key, value in self.unique_words.items():
                    if value == choice:

                        print('Choice #%.05d probability %.5f > Rand probability %.5f -> Word chosen: \"%s\"' % (
                                iterations, \
                                choice_prob, \
                                random_prob,\
                                key))

                        next_word = key

                        return next_word


def main():

    # Generate a list of definitions from a text file of Websters dictionary
    list_of_defs = clean_text()

    # Instantiate def_gen class and provide it list of definitions
    dg = def_gen(list_of_defs)

    # Create index of unique words found in definitions
    dg.create_index_of_words()

    # Create transition matrix based on the definitions found in the dictionary
    dg.create_trans_matrix()

    current_word = 'start_of_definition'
    output_def = 'Definition: '

    while True:
        next_word = dg.get_next_word(current_word)

        # If definition is over, print definition and prompt for re-run
        if next_word == 'end_of_definition':

            print(output_def)
            print()

            answer = input("Generate another definition? (y/n) ")

            if answer in ["Y", "y", "yes"]:
                current_word = 'start_of_definition'
                output_def = 'Definition: '
                continue

            else:
                return

        # If definition is not over, add word to definition and loop
        else:
            output_def += next_word + ' '
            current_word = next_word

main()
