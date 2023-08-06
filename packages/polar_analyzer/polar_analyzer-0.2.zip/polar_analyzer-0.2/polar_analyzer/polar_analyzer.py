import nltk.tokenize
from collections import Counter
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from nltk.corpus import wordnet
from nltk import WordPunctTokenizer
from nltk.tokenize import RegexpTokenizer
import re
import statistics

class polar_analyzer:
    
    def __init__(self):
        self.values = list()
        self.data = ""
        
    def read_file(self, fileName):
        with open(fileName, 'r') as f:
            self.data = f.read()
       
    def read_string(self, string):
        self.data = string
        
    def polar_values(self, positive_seeds, negative_seeds):
        POS_tags = list(set(nltk.pos_tag(WordPunctTokenizer().tokenize(self.data))))
        words = []
        for (w, s) in POS_tags:
           w= w.lower()
           POS =  self.get_wordnet_pos(s)
           if POS =='' or re.match("^[\w]+$",w) == None:
               words.append('0')
           else:
               w+="."+POS
               w+=".01"
               words.append(w)
        negative_set = []
        for nw in negative_seeds:
            for s in wordnet.synsets(nw):
                negative_set.append(s)

        for pw in positive_seeds:
            for s in wordnet.synsets(pw):
                positive_set.append(s)
        positive_set = tmp
        self.eval_words(words, positive_set, negative_set)
        return self.values
    
    def eval_words(self, words, positive_set, negative_set):
        for word in words:
            if word == '0':
                self.values.append(0)
            else:
                Original_word = word.split(".")[0]

                synsets = wordnet.synsets(Original_word)
                synset = [s for s in synsets if s.name() == word]

                if synset != []:
                    P_score = self.get_closest_relation(synset[0], positive_sets)
                    N_score = self.get_closest_relation(synset[0], negative_sets)
                elif synsets !=[]:  
                    P_score = self.get_closest_relation(synsets[0], positive_sets)
                    N_score = self.get_closest_relation(synsets[0], negative_sets)
                else:
                    P_score = N_score = 0
                self.values.append(P_score if P_score > N_score else -1*N_score)
    
    def get_closest_relation(self, wordset, synsets):
        score =0
        for synset in synsets:
            sim = synset.wup_similarity(wordset)
            if sim!= None:
                score = max(score, sim)
        return score
    
    def get_wordnet_pos(treebank_tag):
        print(treebank_tag)
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return ''
        
    def plot(self, fileName, wordsPerPoint = 20):
        pass
    
