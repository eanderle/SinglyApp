# Custom Sentiment Analysis for Singly Hackathon
# Author: Rami Sayar
__author__ = 'Rami Sayar'

import nltk
import nltk.classify.util

class SentimentClassifier(object):
    classifier = None
    word_features = None

    def __init__(self):
        self.classifier = None
        self.word_features = None

    def train(self, data):
        self.word_features = self.get_word_features(self.get_words_in_data(data))
        training_set = nltk.classify.util.apply_features(self.extract_features, data)
        self.classifier = nltk.NaiveBayesClassifier.train(training_set)

    def classify(self, data):
        return self.classifier.classify(self.extract_features(data.split()))
    
    def get_words_in_data(self, data):
        all_words = []
        for (words, sentiment) in data:
            all_words.extend(words)
        return all_words

    def get_word_features(self, wordlist):
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features

    def extract_features(self, document):
        document_words = set(document)
        features = {}
        for word in self.word_features:
            features['contains(%s)' % word] = (word in document_words)
        return features

    def get_accuracy(self, test_data):
        return nltk.classify.accuracy(self.classifier, test_data)

    def get_most_informative_features(self):
        return self.classifier.show_most_informative_features(200)

if __name__ == '__main__':
    pos_tweets = [('I love this car', 'positive'), 
                  ('This view is amazing', 'positive'), 
                  ('I feel great this morning', 'positive'),
                  ('I am so excited about the concert', 'positive'),
                  ('He is my best friend', 'positive')]

    neg_tweets = [('I do not like this car', 'negative'),
                  ('This view is horrible', 'negative'),
                  ('I feel tired this morning', 'negative'),
                  ('I am not looking forward to the concert', 'negative'),
                  ('He is my enemy', 'negative')]

    test_tweets = [
        (['feel', 'happy', 'this', 'morning'], 'positive'),
        (['larry', 'friend'], 'positive'),
        (['not', 'like', 'that', 'man'], 'negative'),
        (['house', 'not', 'great'], 'negative'),
        (['your', 'song', 'annoying'], 'negative')]

    tweets = []
    for (words, sentiment) in pos_tweets + neg_tweets:
        words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
        tweets.append((words_filtered, sentiment))
    
    import pprint
    pprint.pprint(tweets)

    feelings = SentimentClassifier()
    feelings.train(tweets)
    
    pprint.pprint(feelings.classify('Larry is my friend'))
    pprint.pprint(feelings.classify('I do not like this car.'))
    
    print feelings.get_most_informative_features() 
