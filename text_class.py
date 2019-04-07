# importing modules and libraries

from sklearn import metrics
from sklearn.metrics import confusion_matrix
import seaborn as sns
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.feature_selection import chi2
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from io import StringIO
import pandas as pd
from random import shuffle

# for converting sql database into csv data for test set.
import pymysql



# reading data for trainig the model.
df = pd.read_csv("DATASET/Dataset1.csv")

df = df[['event_name', 'category', 'category_id']]

# defining not null value for any object
df = df[pd.notnull(df['event_name'])]

# this is the features
df.columns = ['event_name', 'category', 'category_id']

# encoding the object as an enumerated type according to category
df['category_id'] = df['category'].factorize()[0]

# Return DataFrame with duplicate rows removed
category_id_df = df[['category', 'category_id']].drop_duplicates().sort_values('category_id')

category_to_id = dict(category_id_df.values)

id_to_category = dict(category_id_df[['category_id', 'category']].values)



# dealing with imbalanced classifiaction
# to see the differnt catogry that is being used for traing the model

fig = plt.figure(figsize=(8, 6))
df.groupby('category').event_name.count().plot.bar(ylim=0)
plt.show()


# applying bag of words approach
# tfidf = term frequency inverse document frequency it besically shows how important is a word to the document
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2',encoding='latin-1', ngram_range=(1, 3), stop_words='english')

# features is input and label is output
features = tfidf.fit_transform(df.event_name).toarray()
# this is the label
labels = df.category_id

# print("The shape of the feature is ",features.shape)

# to find the terms which are most correlated with each of the event
N = 2
for category, category_id in sorted(category_to_id.items()):
    features_chi2 = chi2(features, labels == category_id)
    indices = np.argsort(features_chi2[0])
    feature_names = np.array(tfidf.get_feature_names())[indices]
    unigrams = [v for v in feature_names if len(v.split(' ')) == 1]
    bigrams = [v for v in feature_names if len(v.split(' ')) == 2]
    print("# '{}':".format(category))
    print("  . Most correlated unigrams:\n. {}".format('\n. '.join(unigrams[-N:])))
    print("  . Most correlated bigrams:\n. {}".format('\n. '.join(bigrams[-N:])))


# Multi-Class Classifier: feature and design
# we first transforemed the into a vector of numbers.
# we explored vector representation such as TF-IDF weighted vectors

X_train, X_test, y_train, y_test = train_test_split(df['event_name'], df['category'], random_state=0,shuffle = True)
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

# model evaluation
model = LinearSVC(C=1.0, class_weight=None, dual=True, fit_intercept=True,
     intercept_scaling=1, loss='squared_hinge', max_iter=10000,
     multi_class='ovr', penalty='l2', random_state=5, tol=1e-05, verbose=0)

# fitting the model to the specified data given
clf = model.fit(X_train_tfidf, y_train)

# <!!! End of traing the model now just need to provide the data that is being crawled as a test set for classification


# for converting the crawled data into csv format data for classifying different events
conn = pymysql.connect(server='', port='', user='', password='', database='')
cursor = conn.cursor()

# your_table_name = required name of the table that you want to convert it into csv file
query = 'select * from your_table_name'

cursor.execute(query)

# writing content of the sql database into csv file 
# this file will be the input of the model
with open("test.csv","w") as outfile:
    writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(col[0] for col in cursor.description)
    for row in cursor:
        writer.writerow(row)


df_predict = pandas.read_csv('test.csv')
df['category'] = clf.predict(count_vect.transform(description))


# predict the cateogory of different description according to the dataset
pred  = df[['event_name','category','description']]


# converting the prediction into csv format and writing to the file.
pred.to_csv('predict.csv', sep=',', encoding='utf-8',index = False)



print(clf.predict(count_vect.transform(df_class)))


# just for analysing graphically the prediction given by the model through cinfusion matrix.

X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(
    features, labels, df.index, test_size=0.20, random_state=5)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
conf_mat = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(10, 10))
sns.heatmap(conf_mat, annot=True, fmt='d',
    xticklabels=category_id_df.category.values, yticklabels=category_id_df.category.values)
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()


model.fit(features, labels)
N = 2
for category, category_id in sorted(category_to_id.items()):
    indices = np.argsort(model.coef_[category_id])
    feature_names = np.array(tfidf.get_feature_names())[indices]
    unigrams = [v for v in reversed(feature_names) if len(v.split(' ')) == 1][:N]
    bigrams = [v for v in reversed(feature_names) if len(v.split(' ')) == 2][:N]
    print("# '{}':".format(category))
    print("  . Top unigrams:\n       . {}".format('\n       . '.join(unigrams)))
    print("  . Top bigrams:\n       . {}".format('\n       . '.join(bigrams)))

print(metrics.classification_report(y_test, y_pred, target_names=df['category'].unique()))

