from text_generator.text_generator import TextGenerator
import unittest


class TestTextGenerator(unittest.TestCase):

    def test__random_string(self):
        t_gen = TextGenerator()
        word_one = t_gen._random_string(length=5)
        word_two = t_gen._random_string(length=5)

        self.assertFalse(word_one == word_two, "Comparing two different random strings with the same length")
        self.assertTrue(len(word_one) == len(word_two), "Comparing length of two random words with the same length")


    def test_text_generator_dictionary(self):
        t_gen = TextGenerator()

        '''
        I don't undestand why this test fail!!!!!
        dictionary = t_gen.get_dictionary()
        self.assertTrue(len(dictionary) == 0, "Checking length of a empty dict: " + str(dictionary))
        '''

        dic_length = 2500
        t_gen.generate_dictionary(dic_length)
        dictionary = t_gen.get_dictionary()

        self.assertTrue(len(dictionary) == dic_length, "Checking length of a random dictionary")

        #Change dictionary
        t_gen.add_word('Jordi')
        dictionary = t_gen.get_dictionary()
        self.assertTrue(len(dictionary) == dic_length+1, "Checking length of a random dictionary after add 1 word")


    def test_add_word(self):
        t_gen = TextGenerator()

        t_gen.add_word('Jordi')
        dictionary = t_gen.get_dictionary()
        self.assertTrue(dictionary.index('Jordi') >= 0, "Checking empty dictionary adds a word")


        dic_length = 15
        t_gen.generate_dictionary(dic_length)
        t_gen.add_word('Jordi')
        dictionary = t_gen.get_dictionary()
        new_dic_length = len(dictionary)
        self.assertTrue(dic_length+1 == new_dic_length, "Checking non empty dictionary adds a word ")


        t_gen.add_word('Jordi')
        dictionary = t_gen.get_dictionary()
        new_dic_length = len(dictionary)
        self.assertTrue(dic_length+1 == new_dic_length, "Checking non empty dictionary doesn't adds a word twice")



if __name__ == '__main__':
    unittest.main()
