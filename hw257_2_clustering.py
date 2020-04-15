# -*- coding: utf-8 -*-
"""hw257#2_clustering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DToDyt5Ssjs541LiqJUrXJIDz2u5jFXb
"""

from google.colab import drive
drive.mount('/content/drive')

#Importing required packages
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split as tts
from sklearn.preprocessing import StandardScaler as ss
import itertools
from scipy import linalg
import matplotlib as mpl

#Reading in the data as a Pandas dataframe
df = pd.read_csv("/content/drive/My Drive/MLSpring2020/AIInsight_CrunchbasePrediction/Datasets/wine.csv")

df.info()

df.shape

"""first 10 rows"""

df.head(10)

df.tail(10)

df.describe()

correlation=df.corr()
plt.figure(figsize=(25,25))
sns.heatmap(correlation,annot=True,cmap='coolwarm')

sns.lmplot('Alcohol','Proline',data=df, hue='Target',
           palette='coolwarm',size=6,aspect=1,fit_reg=False)

sns.set_style('darkgrid')
g = sns.FacetGrid(df,hue="Target",palette='coolwarm',size=6,aspect=2)
g = g.map(plt.hist,'Alcohol',bins=20,alpha=0.7)

# split into training and testing datasets
X, y = df.iloc[:, 1:].values, df.iloc[:, 0].values
X_train, X_test, y_train, y_test = tts(X, y, test_size=0.3,stratify=y, random_state=0)
print(X_train)
print(y_train)

"""PCA"""

# standardize the features
sc = ss()
X_train_std = sc.fit_transform(X_train)
X_test_std = sc.transform(X_test)

#obtain the eigenpairs of the Wine covariance matrix:
#data_cov = np.dot(np.transpose(data.values),data.values)
#data_cov
X_train_cov = np.cov(X_train_std.T)
w, v = np.linalg.eig(X_train_cov)

w

#The percent of variability contained within each component
w_percent = (w/np.sum(w))*100                 
print(w, '-> eigenvalues')
print(w_percent, ' -> percent of variability explained')

# calculate cumulative sum of explained variances
tot = sum(w)
var_exp = [(i / tot) for i in sorted(w, reverse=True)]
cum_var_exp = np.cumsum(var_exp)

# plot explained variances
plt.title("Component-wise and Cumulative Explained Variance")
plt.bar(range(1,14), var_exp, alpha=0.5,
        align='center', label='individual explained variance')
plt.step(range(1,14), cum_var_exp, where='mid',
         label='Percentage of variability explained')
plt.ylabel('Explained variance ratio')
plt.xlabel('Principal component index')
plt.legend(loc='best')
plt.show()

# Make a list of (eigenvalue, eigenvector) tuples
eigen_pairs = [(np.abs(w[i]), v[:, i]) for i in range(len(w))]

# Sort the (eigenvalue, eigenvector) tuples from high to low
eigen_pairs.sort(key=lambda k: k[0], reverse=True)
w2 = np.hstack((eigen_pairs[0][1][:, np.newaxis], eigen_pairs[1][1][:, np.newaxis]))
print('Matrix W2:\n', w2)

X_train_pca = X_train_std.dot(w2)
print(X_train_pca)

colors = ['green', 'blue', 'red']
markers = ['s', 'x', 'o']
for l, c, m in zip(np.unique(y_train), colors, markers):
    plt.scatter(X_train_pca[y_train==l, 0], X_train_pca[y_train==l, 1], c=c, label=l, marker=m) 
plt.xlabel('PC 1')
plt.ylabel('PC 2')
plt.legend(loc='lower left')
plt.show()

"""K-means"""

from sklearn.cluster import KMeans
from numpy import *
import matplotlib

"""finding the best k"""

sum_of_squared = []
K = range(1,15)
for k in K:
    km = KMeans(n_clusters=k)
    km = km.fit(X_train_std)
    sum_of_squared.append(km.inertia_)
plt.figure(figsize=(20,5))
plt.plot(K, sum_of_squared, 'bx-')
plt.xlabel('k')
plt.ylabel('Sum_of_squared_distances')
plt.title('Elbow Method For Optimal k')
plt.show()

"""#so we can find the k=3 best here"""

kmeans=KMeans(algorithm='auto', copy_x=True, init='k-means++', max_iter=100,
       n_clusters=3, n_init=5, n_jobs=None, precompute_distances='auto',
       random_state=None, tol=0.0001, verbose=0)

kmeans.fit(df.drop('Target',axis=1))

kmeans.fit_predict(X_train_std)
print(kmeans.labels_)
plt.scatter(X_train_std[:,0],X_train_std[:,1], c=kmeans.labels_, cmap='rainbow')
plt.title("kmeans")

"""AffinityPropagation"""

from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.datasets import make_blobs

af = AffinityPropagation(preference=-50).fit(X_train_std)
cluster_centers_indices = af.cluster_centers_indices_
labels = af.labels_

n_clusters_ = 3

# Commented out IPython magic to ensure Python compatibility.
print('number of clusters: %d' % n_clusters_)
print("Homogeneity: %0.3f" % metrics.homogeneity_score(y_train, labels))
print("Completeness: %0.3f" % metrics.completeness_score(y_train, labels))
print("V-measure: %0.3f" % metrics.v_measure_score(y_train, labels))
print("Adjusted Rand Index: %0.3f"
#       % metrics.adjusted_rand_score(y_train, labels))
print("Adjusted Mutual Information: %0.3f"
#       % metrics.adjusted_mutual_info_score(y_train, labels))
print("Silhouette Coefficient: %0.3f"
#       % metrics.silhouette_score(X_train_std, labels, metric='sqeuclidean'))

# Plot result
import matplotlib.pyplot as plt
from itertools import cycle

plt.close('all')
plt.figure(1)
plt.clf()

colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
for k, col in zip(range(n_clusters_), colors):
    class_members = labels == k
    cluster_center = X_train_std[cluster_centers_indices[k]]
    plt.plot(X_train_std[class_members, 0], X_train_std[class_members, 1], col + '.')
    plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)
    for x in X_train_std[class_members]:
        plt.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], col)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()



"""GMM"""

from sklearn import mixture

gmm = mixture.GaussianMixture(n_components=3).fit(X_train_std)

labels = gmm.predict(X_train_std)
plt.scatter(X_train_std[:, 0], X_train_std[:, 1], c=labels, s=40, cmap='viridis');
plt.title("GMM")