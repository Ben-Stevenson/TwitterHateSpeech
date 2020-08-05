# -*- coding: utf-8 -*-
"""Davidson.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZcdVNZHJDb0-nAS4Kcge82FfyuWFVOJl
"""

import pandas as pd
import csv
import nltk
from nltk.tokenize import TweetTokenizer
nltk.download('averaged_perceptron_tagger')
from nltk.stem import PorterStemmer
import re
from sklearn.feature_selection import chi2
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn import svm
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
nltk.download('punkt')
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from nltk import ngrams
from numbers import Number

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import fbeta_score
from sklearn.metrics import classification_report
def eval_summary(name, predictions, labels):
  
  precision = precision_score(predictions, labels,average='macro')
  recall = recall_score(predictions, labels,average='macro')
  accuracy = accuracy_score(predictions, labels)
  f1 = fbeta_score(predictions, labels, 1,average='macro') #1 means f_1 measure

  print("Classifier '%s' has P=%0.3f R=%0.3f Acc=%0.3f F1=%0.3f" % (name,precision,recall,accuracy,f1))
  print(classification_report(predictions, labels))


def perf_measure(y_actual, y_pred):
    TP = 0
    FP = 0
    TN = 0
    FN = 0

    for i in range(len(y_pred)): 
        if y_actual[i]==y_pred[i]==1:
           TP += 1
        if y_pred[i]==1 and y_actual[i]!=y_pred[i]:
           FP += 1
        if y_actual[i]==y_pred[i]==0:
           TN += 1
        if y_pred[i]==0 and y_actual[i]!=y_pred[i]:
           FN += 1

    return("TP: {TP} FP: {FP}  TN: {TN} FN: {FN}").format(TP = TP,FP =FP,TN=TN,FN=FN)

read = pd.read_csv("labeled_data.csv")
data = pd.DataFrame({'label':read['Label'],
                              'text':read["Text"].replace(r'\n',' ',regex=True)
                             })

"""# TEXT CLASSIFICATION"""

hate_speech = pd.read_csv("refined_ngram_dict.csv")

hate_speech = hate_speech['ngram']
hate_terms = []
to_list = [hate_terms.append(words) for words in hate_speech]

def char_three(sentence):
  p = re.findall(r'((\w)\2{2,})', sentence)
  if bool(p):
    for i in range(len(p)):
      sentence = sentence.replace(p[i][0],p[i][1])
  return(sentence)

from nltk.corpus import stopwords
nltk.download('stopwords')
stopWords = set(stopwords.words('english'))
ps = PorterStemmer()
tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)

tknzr.tokenize("Hello!! my name is ben. What is your name? :)")

def processing(train_df):
  train_df['label'] = train_df['label_id'].map({0: "Hate", 1: "Offensive",2:"Neither"})
  train_df['length'] = train_df['text'].apply(lambda x: len(x))

  train_df['processed'] = train_df['text'].apply(lambda x: re.sub(r'[^\w\s]','', x.lower()))
  train_df['processed'] = [char_three(sentence) for sentence in train_df['processed']] 

  train_df['pos_tag'] = [tknzr.tokenize(lines) for lines in train_df['processed']]
  train_df['pos_tag'] = [nltk.pos_tag(words) for words in train_df['pos_tag']]
  train_df['pos_tag'] = [[words[1] for words in tuples] for tuples in train_df['pos_tag']]
  train_df['pos_tag'] = [" ".join(words) for words in train_df['pos_tag']]
  train_df['unigram'] = [[item for item in ngrams(sent.split(),n)] for n in range(1,2) for sent in train_df['processed']]
  train_df['unigram'] = [" ".join([" ".join(unigram) for unigram in items]) for items in train_df['unigram']]
  train_df['bigram'] = [[item for item in ngrams(sent.split(),n)] for n in range(2,3) for sent in train_df['processed']]
  train_df['bigram'] = [" ".join([" ".join(bigram) for bigram in items]) for items in train_df['bigram']]
  train_df['trigram'] = [[item for item in ngrams(sent.split(),n)] for n in range(3,4) for sent in train_df['processed']]
  train_df['trigram'] = [" ".join([" ".join(bigram) for bigram in items]) for items in train_df['trigram']]
  # train_df['processed'] = train_df['processed'].apply(lambda x: [ps.stem(y) for y in x])
  
  # train_df['processed'] = [" ".join(line) for line in train_df['processed']]
  train_df['Chars'] = train_df['processed'].apply(lambda x: len(x))
  train_df['words'] = train_df['processed'].apply(lambda x: len(x.split(' ')))

  
  train_df['avg_word_length'] = train_df['processed'].apply(lambda x: np.mean([len(t) for t in x.split(' ') if t not in stopWords]) if len([len(t) for t in x.split(' ') if t not in stopWords]) > 0 else 0)
  train_df['avg_sent_length'] = train_df['text'].apply(lambda x: np.mean([len(t.split()) for t in x.split(".")]))
  return(train_df)

def splitTextToTuple(string, n):
    words = string.split()
    grouped_words = [' '.join(words[i: i + n]) for i in range(0, len(words), n)]
    return grouped_words

sentence = "hello I love to read lots and lots of book s"
print(splitTextToTuple(sentence, 4))

df = processing(train_df)

# df_test = df

hate_uni = [words for words in hate_terms if len(words.split()) == 1]
hate_bi = [words for words in hate_terms if len(words.split()) == 2]
hate_tri = [words for words in hate_terms if len(words.split()) == 3]


import inspect
# def count_hate(n):
def var_to_string(var):
  for fi in reversed(inspect.stack()):
            names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
            if len(names) > 0:
                return names[0]

def count_hate(column, n, hate_ngram, dataframe):
  column_name = "hate_" + var_to_string(hate_ngram).split("_")[1]
  dataframe[column_name] = [splitTextToTuple(sentence, n) for sentence in dataframe[column]]
  
  
  index = 0
  
  # dataframe[column_name] = count
  for lists in dataframe[column_name]:
    # print(lists)
    count = 0
    
    for ngram in lists:
      if ngram in hate_ngram:
        count+=1
        dataframe.at[index, column_name] = count
    index+=1
  x = [items for items in dataframe[column_name] if isinstance(items, list)==False]
  index = 0
  for rows in dataframe[column_name]:
    if rows not in x:
      dataframe.at[index, column_name] = 0
    index+=1
  
  return(dataframe)
df = count_hate('unigram', 1, hate_uni, df)

df = count_hate('bigram', 2, hate_bi, df)

df = count_hate('trigram', 3, hate_tri, df)
df['hate_tri'].value_counts()



features= [c for c in df.columns.values if c  not in ['text','label_id']]
numeric_features= [c for c in df.columns.values if c  not in ['text','label_id','processed']]
target = 'label_id'
  
X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, random_state=42)
X_train.head()





from sklearn.base import BaseEstimator, TransformerMixin
from collections import Counter

class TextSelector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a single column from the data frame to perform additional transformations on
    Use on text columns in the data
    """
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[self.key]
    
class NumberSelector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a single column from the data frame to perform additional transformations on
    Use on numeric columns in the data
    """
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[[self.key]]

    
class PosTagMatrix(BaseEstimator, TransformerMixin):
    #normalise = True - devide all values by a total number of tags in the sentence
    #tokenizer - take a custom tokenizer function
    def __init__(self, tokenizer=lambda x: x.split(), normalize=True):
        self.tokenizer=tokenizer
        self.normalize=normalize

    #helper function to tokenize and count parts of speech
    def pos_func(self, sentence):
        return Counter(tag for word,tag in nltk.pos_tag(self.tokenizer(sentence)))

    # fit() doesn't do anything, this is a transformer class
    def fit(self, X, y = None):
        return self

    #all the work is done here
    def transform(self, X):

        X_tagged = X.apply(self.pos_func).apply(pd.Series).fillna(0)
        X_tagged['n_tokens'] = X_tagged.apply(sum, axis=1)
        if self.normalize:
            X_tagged = X_tagged.divide(X_tagged['n_tokens'], axis=0)
        
        return X_tagged

class AverageWordLengthExtractor(BaseEstimator, TransformerMixin):
    """Takes in dataframe, extracts road name column, outputs average word length"""

    def __init__(self):
        pass

    def average_word_length(self, name):
        """Helper code to compute average word length of a name"""
        return np.mean([len(word) for word in name.split()])

    def transform(self, df, y=None):
        """The workhorse of this feature extractor"""
        return df['label_id'].apply(self.average_word_length)

    def fit(self, df, y=None):
        """Returns `self` unless something different happens in train and test"""
        return self

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

text = Pipeline([
                ('selector', TextSelector(key='processed')),
                ('tfidf', TfidfVectorizer()),
              ])

text.fit_transform(X_train)

pos_tagger = Pipeline([
                    ('selector', TextSelector(key='pos_tag')),
                    ('tfidf', TfidfVectorizer()),
])
pos_tagger.fit_transform(X_train)

uni_gram = Pipeline([
                     ('selector',TextSelector(key='unigram')),
                     ('tfidf',TfidfVectorizer(ngram_range=(1,2))),
])

bi_gram = Pipeline([
                     ('selector',TextSelector(key='bigram')),
                     ('tfidf',TfidfVectorizer(ngram_range=(2,3))),
])

tri_gram = Pipeline([
                     ('selector',TextSelector(key='trigram')),
                     ('tfidf',TfidfVectorizer(ngram_range=(3,4))),
])

from sklearn.preprocessing import StandardScaler

length =  Pipeline([
                ('selector', NumberSelector(key='length')),
                ('standard', StandardScaler())
            ])

length.fit_transform(X_train)

char_count = Pipeline([
                  ('selector', NumberSelector(key = 'Chars')),
                  ('standard', StandardScaler())
])
char_count.fit_transform(X_train)

words =  Pipeline([
                ('selector', NumberSelector(key='words')),
                ('standard', StandardScaler())
            ])
words.fit_transform(X_train)
words_not_stopword =  Pipeline([
                ('selector', NumberSelector(key='words_not_stopword')),
                ('standard', StandardScaler())
            ])
avg_word_length =  Pipeline([
                ('selector', NumberSelector(key='avg_word_length')),
                ('standard', StandardScaler())
            ])
avg_sent_length =  Pipeline([
                ('selector', NumberSelector(key='avg_sent_length')),
                ('standard', StandardScaler()),
            ])

uni_hate = Pipeline([
                     ('selector', NumberSelector(key="hate_uni")),
                     ('standard', StandardScaler())
])
bi_hate = Pipeline([
                    ('selector', NumberSelector(key="hate_bi")),
                    ('standard', StandardScaler())
])
tri_hate = Pipeline([
                     ('selector', NumberSelector(key="hate_tri")),
                     ('standard', StandardScaler())
])

feats = FeatureUnion([('text', text),
                      ('uni_hate', uni_hate),
                      ('bi_hate', bi_hate),
                      ('tri_hate', tri_hate),
                      ('pos_tagger', pos_tagger), 
                      # ('unigram',uni_gram),
                      # ('bigram', bi_gram),
                      # ('trigram', tri_gram),
                      ('length', length),
                      ('words', words),
                      ('chars', char_count),
                      ('avg_word_length', avg_word_length),
                      # ('avg_sent_length', avg_sent_length)
                      ])

feature_processing = Pipeline([('feats', feats)])
feature_processing.fit_transform(X_train)

from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB

pipeline = Pipeline([
    ('features',feats),
    
    ('clf', LogisticRegression(penalty="none",max_iter=1000)),
])

pipeline.fit(X_train, y_train)

preds = pipeline.predict(X_test)

from sklearn.metrics import balanced_accuracy_score


print("BAC score: ",balanced_accuracy_score(y_test, preds))

print(classification_report(y_test, preds, target_names = ["Hate","Offensive","Neither"]))

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
conf_mat = confusion_matrix(y_test, preds )



# 0.901



ax = plt.subplot()

plt.title("Confusion Matrix of the classifier")
cmn = conf_mat.astype('float')/conf_mat.sum(axis=1)[:,np.newaxis]
sns.heatmap(cmn,annot=True, ax = ax, fmt='.2f',cmap='Blues')
ax.yaxis.set_ticklabels(["Hate","Offensive","Neither"])
ax.xaxis.set_ticklabels(["Hate","Offensive","Neither"])
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
plt.show()
plt.draw()





"""# DATA ANALYSIS"""

data['label'].value_counts().sort_values(ascending=False).plot(kind='bar', y='Number of Samples', 
                                                                title='Number of samples for each class')

import pandas as pd
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

nltk.download('wordnet')


# Remove numbers
data['text'] = data['text'].apply(lambda x: re.sub(r'\d+', '', x.lower()))


# Remove Punctuation
data['text']  = data['text'].map(lambda x: x.translate(x.maketrans('', '', string.punctuation)))


# Remove white spaces
data['text'] = data['text'].map(lambda x: x.strip())


# Tokenize into words
data['text'] = data['text'].map(lambda x: word_tokenize(x))

 
# Remove non alphabetic tokens
data['text'] = data['text'].map(lambda x: [word for word in x if word.isalpha()])

# filter out stop words
stop_words = set(stopwords.words('english'))
data['text'] = data['text'].map(lambda x: [w for w in x if not w in stop_words])


# Word Lemmatization
lem = WordNetLemmatizer()
data['text'] = data['text'].map(lambda x: [lem.lemmatize(word,"v") for word in x])


# Turn lists back to string
data['text'] = data['text'].map(lambda x: ' '.join(x))

data['text'] = data['text'].apply(lambda x: re.sub(r'rt', '', x))

data['label'][data['label'] == 0] = 'hate'
data['label'][data['label'] == 1] = 'offensive'
data['label'][data['label'] == 2] = 'neither'

data.head(5)

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
le.fit(data.label)
data.label = le.transform(data.label)
data.head(5)



from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_title = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')
# tfidf_desc = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')
labels = data.label
features_title = tfidf_title.fit_transform(data.text).toarray()
# features_description = tfidf_desc.fit_transform(data.Description).toarray()
print('Title Features Shape: ' + str(features_title.shape))
# print('Description Features Shape: ' + str(features_description.shape))



from sklearn.feature_selection import chi2
import numpy as np
N = 5
for current_class in ['hate','offensive','neither']:
    current_class_id = le.transform([current_class])[0]
    features_chi2 = chi2(features_title, labels == current_class_id)
    indices = np.argsort(features_chi2[0])
    feature_names = np.array(tfidf_title.get_feature_names())[indices]
    unigrams = [v for v in feature_names if len(v.split(' ')) == 1]
    bigrams = [v for v in feature_names if len(v.split(' ')) == 2]
  
    print("# '{}':".format(current_class))
    print("Most correlated unigrams:")
    print('-' *30)
    print('. {}'.format('\n. '.join(unigrams[-N:])))
    print("Most correlated bigrams:")
    print('-' *30)
    print('. {}'.format('\n. '.join(bigrams[-N:])))
    print("\n")

