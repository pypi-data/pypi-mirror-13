import numpy as np
import string
import sys


class TextGenerator():

    # Supported distributions

    distributions_list = ['uniform', 'exponential', 'geometric', 'zipf']

    def __init__(self, dictionary=set({}), probabilities=[], distribution= ''):
        self.dictionary = dictionary
        self.probabilities = probabilities
        self.distribution = distribution

    # Private methods

    @staticmethod
    def _random_string(length=5, pool=[], num=True, upper=True):
        if len(pool) == 0:
            pool = string.ascii_lowercase
            if upper:
                pool += string.ascii_uppercase
            if num:
                pool += string.digits
            pool = list(pool)

        return ''.join([np.random.choice(pool) for n in range(length)])

    def _get_distribution_values(self, distribution, length):
        probabilities = []
        if distribution == 'uniform':
            probabilities = np.random.uniform(0, 1, length)
        elif distribution == 'exponential':
            probabilities = np.random.exponential(0.01, size=length)
        elif distribution == 'geometric':
            probabilities = np.random.geometric(0.01, size=length)
        elif distribution == 'zipfs':
            probabilities = np.random.zipf(1.01, size=length)
        else:
            raise WrongConfigurationError(
                    'There are no distribution assigned to generate the stream')


        #normalize probabilites
        total_sum = sum(probabilities)
        probabilities = [x/total_sum for x in probabilities]
        np.random.shuffle(probabilities)

        return probabilities

    # Public methods

    def add_word(self, word):
        if word not in self.dictionary:
            self.dictionary.add(word)

    def get_dictionary(self):
        return list(self.dictionary)

    def set_dictionary(self, dictionary):
        self.dictionary = set(dictionary)

    def generate_dictionary(self, n_words):
        self.dictionary = set({})
        pool = list(string.ascii_lowercase + string.ascii_uppercase + string.digits)
        for i in np.random.normal(8, 1.5, n_words):
            self.dictionary.add(
                    self._random_string(length=int(i), pool=pool))

    def get_dictionary_len(self):
        return len(self.dictionary)

    def get_distribution_name(self):
        return self.distribution

    def set_distribution(self, distribution):
        if distribution in self.distributions_list:
            self.distribution = distribution
        else:
            raise WrongConfigurationError(
                    'This distribution is not supported: ' + distribution)


    def generate_stream(self, N):
        if len(self.dictionary) != len(self.probabilities):
            self.probabilities =\
                self._get_distribution_values(self.distribution, len(self.dictionary))

        dictionary_list = list(self.dictionary)

        for _ in range(N):
            yield np.random.choice(dictionary_list, p=self.probabilities)



class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class WrongConfigurationError(Error):
    """Exception raised for errors in the configuration.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def usage():
    print('Usage: text_generator n N d')
    print('n: Number of different values')
    print('N: Total values generated')
    print('d: Distribution in [uniform, exponential, geometric, zipfs]')


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    print(args)
    if len(args) != 3:
        usage()
        exit(0)

    else:
        n = int(args[0])
        N = int(args[1])
        distribution = args[2]

        t_gen = TextGenerator(distribution=distribution)
        t_gen.generate_dictionary(n)

        for elem in t_gen.generate_stream(N):
            print(elem)


if __name__ == '__main__':
    main()
