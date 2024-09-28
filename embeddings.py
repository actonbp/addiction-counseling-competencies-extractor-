import json
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns

# Load the JSON data
# Assuming the JSON data is stored in a file named 'competencies.json'
with open("competencies.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract the competency titles
titles = [item["title"] for item in data]

# Initialize the Sentence-BERT model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)  # Efficient model suitable for this task

# Generate embeddings for the titles
embeddings = model.encode(titles)

# Compute cosine similarity matrix
similarity_matrix = cosine_similarity(embeddings)

# Display the similarity matrix as a heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(similarity_matrix, xticklabels=titles, yticklabels=titles, cmap="viridis")
plt.title("Cosine Similarity Between Competency Titles")
plt.xticks(rotation=90)
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# Optionally, perform hierarchical clustering
from scipy.cluster.hierarchy import linkage, dendrogram

# Perform hierarchical clustering
linked = linkage(embeddings, "ward")

# Plot the dendrogram
plt.figure(figsize=(10, 7))
dendrogram(
    linked,
    orientation="top",
    labels=titles,
    distance_sort="descending",
    show_leaf_counts=True,
)
plt.xticks(rotation=90)
plt.title("Hierarchical Clustering Dendrogram of Competency Titles")
plt.tight_layout()
plt.show()

# K-means clustering


from sklearn.cluster import KMeans

# Define the number of clusters
num_clusters = 3  # Adjust as needed

# Fit K-Means clustering
kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(embeddings)

# Assign cluster labels to each title
cluster_labels = kmeans.labels_

# Print competencies grouped by cluster
for cluster_num in range(num_clusters):
    print(f"\nCluster {cluster_num + 1}:")
    for idx, title in enumerate(titles):
        if cluster_labels[idx] == cluster_num:
            print(f" - {title}")


print(f"Number of embeddings: {len(embeddings)}")
