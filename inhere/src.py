# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_src.ipynb.

# %% auto 0
__all__ = ['load_data', 'get_one_hot_encoding', 'reduce_dimensions', 'get_number_of_clusters', 'make_elbow_chart',
           'run_clustering', 'get_cluster_distances', 'run_tsne', 'plot_tsne']

# %% ../nbs/01_src.ipynb 3
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial import distance
from sklearn.manifold import TSNE

import altair as alt

# %% ../nbs/01_src.ipynb 5
def load_data():
	df = pd.read_excel('../data/bnc2014sampleforR.xlsx')
	relevant_columns = [
		'Number of hit',
		'left_context',
		'node',
		'right_context',
		# 'L3_word',
		'L2_word',
		'L1_word',
		'R1_word',
		'R2_word',
		'R3_word',
		'L2_wc',
		'L1_wc',
		'R1_wc',
		'foc',
		'fig',
		'mot',
		'con',
		'van',
		'ill'
	]
	return df[relevant_columns]

# %% ../nbs/01_src.ipynb 7
def get_one_hot_encoding(df, columns: list):
	return pd.get_dummies(df[columns])

# %% ../nbs/01_src.ipynb 9
def reduce_dimensions(df_onehot):
	n_components = min(50, df_onehot.shape[1])  # reduce to 50 components or total features if less than 50
	pca = PCA(n_components=n_components)
	dimred = pca.fit_transform(df_onehot)
	return dimred

# %% ../nbs/01_src.ipynb 11
def get_number_of_clusters(dimred):
    silhouette_scores = []
    # Start from 2 as silhouette score isn't defined for k=1
    for k in range(2, 10):
        kmeans = KMeans(n_clusters=k, n_init=10).fit(dimred)
        labels = kmeans.labels_
        silhouette_scores.append(silhouette_score(dimred, labels))
        optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2
    return optimal_k

# %% ../nbs/01_src.ipynb 12
def make_elbow_chart(dimred, n_max):
    wcss = []
    for i in range(1, n_max+1):
        kmeans = KMeans(
        n_clusters=i, 
        init='k-means++', 
        max_iter=300, 
        n_init=10, 
        random_state=0
        )
        kmeans.fit(dimred)
        wcss.append(kmeans.inertia_)

    df = pd.DataFrame({'Number of clusters': range(1, n_max+1), 'WCSS': wcss})
    elbow_chart = alt.Chart(df).mark_line(point=True).encode(
        x='Number of clusters',
        y='WCSS',
        tooltip=['Number of clusters', 'WCSS']
    ).properties(
        title="Determining the number of clusters based on the Elbow Method"
    )
    return elbow_chart

# %% ../nbs/01_src.ipynb 13
def run_clustering(dimred, k):
    kmeans = KMeans(n_clusters=k, random_state=42)
    clusters = kmeans.fit_predict(dimred)
    centers = kmeans.cluster_centers_
    return clusters, centers

# %% ../nbs/01_src.ipynb 14
def get_cluster_distances(df, dimred, centers):
	for i, center in enumerate(centers):
		dists_atts = []
		for att in dimred:
			dists_atts.append(distance.euclidean(center, att))
		df[f'dist_cluster_{i}'] = dists_atts
	return df

# %% ../nbs/01_src.ipynb 16
def run_tsne(dimred):
	tsne = TSNE(n_components=2, random_state=42)
	tsne_values = tsne.fit_transform(dimred)
	df_tsne = pd.DataFrame(tsne_values, columns=['x', 'y'])
	return df_tsne

# %% ../nbs/01_src.ipynb 17
def plot_tsne(df_tsne, clusters):
	df_tsne['cluster'] = clusters
	chart = alt.Chart(df_tsne).mark_point().encode(
		x='x',
		y='y',
		color='cluster:N'
	)
	return chart
