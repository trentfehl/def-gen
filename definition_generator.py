import numpy as np
from tqdm import tqdm

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

    trans_mat = np.load("transition_matrix.npy", mmap_mode = "r")

    print(type(trans_mat))
    print(trans_mat.size)
    print(trans_mat.shape)

    return

"""

    for i in range(number):
        definition = response(word_dict, weight_matrix)
        print "definition: %s" % definition

"""
main()
