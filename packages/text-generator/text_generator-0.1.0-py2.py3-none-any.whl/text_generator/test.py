from text_generator import TextGenerator


k = 100
t_gen = TextGenerator(distribution='uniform')

t_gen.generate_dictionary(k)

vec = []
for elem in t_gen.generate_stream(100*k):
    print(elem)


