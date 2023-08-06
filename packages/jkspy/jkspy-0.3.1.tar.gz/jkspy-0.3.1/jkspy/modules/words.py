import random
from collections import OrderedDict
from jkspy.helpers import strToInt, intToStr

REGULAR_CONSONANTS = list('bcdfgjklmnpqrstvz')
SPECIAL_CONSONANTS = list('hwy')
COMPOSITE_CONSONANTS = ['bl', 'br',
                        'cl', 'cr',
                        'dr',
                        'fl', 'fr',
                        'gl', 'gr',
                        'kl', 'kn', 'kr',
                        'pl', 'pr',
                        'qu',
                        'sc', 'sk', 'sl', 'sm', 'sn', 'sp', 'sq', 'sr', 'st', 'sv',
                        'tr', 'tr', 'ts',
                        'vl', 'vr',]
ENDING_CONSONANTS = ['ck', 'ct',
                     'ft',
                     'gn',
                     'kt',
                     'lb', 'ld', 'lf', 'lk', 'll', 'lm', 'ln', 'lp', 'lt',
                     'mb', 'mp', 'mt',
                     'nc', 'nd', 'nf', 'ng', 'nk', 'nt',
                     'pt',
                     'rb', 'rc', 'rd', 'rf', 'rg', 'rk', 'rl', 'rm', 'rn', 'rp', 'rt', 'rv',
                     'sc', 'sk', 'sm', 'sp', 'st',
                     'tl',
                     'wb', 'wd', 'wf', 'wg', 'wk', 'wl', 'wm', 'wn', 'wp', 'wr', 'wt',]
ADDON_ENDING_CONSONANTS = list('hsz')

REGULAR_VOWELS = list('aeiouy')
COMPOSITE_VOWELS = ['ae', 'ai', 'ao', 'au', 'ay',
                    'ea', 'ee', 'ei', 'eo', 'eu', 'ey',
                    'ia', 'ie', 'io', 'iu', 'iy',
                    'oa', 'oe', 'oi', 'oo', 'ou', 'oy',
                    'ua', 'ue', 'ui', 'uo', 'uy',
                    'ya', 'ye', 'yi', 'yo', 'yu',]

class Generator():
    seed = None
    def __init__(self, seed=None):
        super(Generator, self).__init__()
        if seed:
            random.seed(seed)
            self.seed = seed
        
    def randSyllable(self):
        c1_dice = ( random.random() < 0.91 ) #Chance that a regular consonant will start the syllable
        s1_dice = ( random.random() < 0.05 ) #Chance that a special conjunction consonant is used
        v1_dice = ( random.random() < 0.85 ) #Chance that a regular vowel will be used
        c2_add_dice = ( random.random() < 0.28 ) #Chance that it has an ending consonant
        c2_dice = ( random.random() < 0.91 ) #Chance that a regular consonant will end the syllable
        s2_dice = ( random.random() < 0.03 ) #Chance that the ending has an addon consonant
        
        c1 = random.choice(REGULAR_CONSONANTS) if c1_dice else random.choice(COMPOSITE_CONSONANTS)
        s1 = random.choice(SPECIAL_CONSONANTS) if s1_dice else ''
        v1 = random.choice(REGULAR_VOWELS) if v1_dice else random.choice(COMPOSITE_VOWELS)
        c2 = ( random.choice(REGULAR_CONSONANTS) if c2_dice else random.choice(ENDING_CONSONANTS) ) if c2_add_dice else ''
        s2 = random.choice(ADDON_ENDING_CONSONANTS) if s2_dice else ''
        syllable = c1+s1+v1+c2+s2
#         print(syllable)
        return syllable
    
    def randWord(self, s=2):
        """ s = number of syllables in int """
        word = ''
        for syllable in range(0, s):
            word += self.randSyllable()
        return word
    
    def randSentence(self, meter=[2, 2, 1, 2, 3, 2, 1, 2, 2]):
        sentence = []
        for syllable in meter:
            sentence.append(self.randWord(syllable))
        return ' '.join(sentence)
    
    def randParagraph(self):
        paragraph = []
        rand_wordcount = [ random.randint(3, 6) for i in range(0, random.randint( 4, 5 )) ]
        for words in rand_wordcount:
            rand_meter = [ random.randint(1, 4) for i in range(0, words) ]
            sentence = self.randSentence(rand_meter)
            paragraph.append(sentence)
        return '. '.join(paragraph)
    
    def randDictionary(self, word_list=['apple', 'banana', 'cake', 'dog', 'elephant', 'fruit', 'guava', 'human', 'island', 'joke', 'king', 'love', 'mother', 'nature', 'ocean', 'pie', 'queen', 'random', 'start', 'tree', 'up', 'vine', 'wisdom', 'yellow', 'zoo' ]):
        rand_dict_e2r = { word: self.randWord() for word in word_list }
        rand_dict_r2e = { v: k for k, v in rand_dict_e2r.items() }
        ordered_e2r = OrderedDict()
        print("English to Random Language")
        for key in sorted(rand_dict_e2r.keys()):
            print(key+ ' : '+rand_dict_e2r[key])
            ordered_e2r[key] = rand_dict_e2r[key]
        ordered_r2e = OrderedDict()
        print("\n\nRandom Language to English")
        for key in sorted(rand_dict_r2e.keys()):
            print(key+ ' : '+rand_dict_r2e[key])
            ordered_r2e[key] = rand_dict_r2e[key]
        return ( ordered_e2r, ordered_r2e )
    
    def convertWord(self, word):
        print( strToInt(word) )
        return word