import argparse
import json
import math
import os
import os.path
from pprint import pprint
import sys
import matplotlib.pyplot as pl
import numpy as np
from PIL import Image
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import scipy.ndimage
from tqdm import tqdm

import joblib
import multiprocessing

n_cores = multiprocessing.cpu_count()


def do_pca(X, n):
  pca = PCA(n)
  Xp = pca.fit_transform(X)
  # print(pca.explained_variance_ratio_)
  ax = plt.figure().add_subplot(111, projection='3d')
  ax.scatter(Xp[:,0], Xp[:,1], Xp[:,2])
  plt.show()


def kmeans(X, n):
  pca = PCA(50)
  Xp = pca.fit_transform(X)
  km = KMeans(n)
  labels = km.fit_predict(Xp)


def extract(X):
  freq = X.sum(0)
  plt.plot(freq)
  plt.show()
  freq[freq < np.percentile(freq, 99)] = 0
  f = np.nonzero(freq)[0]
  chosen = X[:, f].argmax(0)


def sharpness(im):
  gray = np.array(im.convert("L")) / 255.0
  var_laplacian = scipy.ndimage.laplace(gray).var()
  return var_laplacian


def sharpness_for_(indices, collection):
  sharpness_delayed = joblib.delayed(sharpness)
  return np.array(joblib.Parallel(n_jobs=n_cores)(sharpness_delayed(collection(i)) for i in indices))


def sharpness_for(indices, collection):
  return np.array([sharpness(collection(i)) for i in tqdm(indices)])


def cluster_for(indices, collection, n_clusters):
  """KMeans on image similarity using downsampled (16x16) images"""
  images = np.array([np.array(collection(i).resize((16,16), resample=Image.NEAREST)) for i in indices]).reshape((len(indices), -1))
  return KMeans(n_clusters=n_clusters).fit_predict(images)


def get_top_frames(features, collection, n=20, k=6):
  # X = features.reshape((-1, 5, features.shape[1])).sum(1).reshape((-1, features.shape[1]))
  X = features
  stop_at = np.where(X.sum(1) == 0)[0][0]
  X = X[:stop_at,:]
  # top_k_idx = X.sum(0).argsort()[::-1][:k]
  top1_idx = X.argmax(1)
  top1_val = X.max(1)
  proportions = np.array([np.sum(top1_idx == i) for i in range(X.shape[1])]) / top1_idx.shape[0]
  top_k_idx = proportions.argsort()[::-1][:k]

  img_indices = []
  for i in top_k_idx:
    idx_for_class = np.where(top1_idx == i)[0]
    val_for_class = top1_val[idx_for_class]
    idx_sorted_for_class = val_for_class.argsort()[::-1][:100]
    idx_sorted = idx_for_class[idx_sorted_for_class]
    img_indices.append(idx_sorted)
  
  top_img = []
  for indices in img_indices:
    cluster = cluster_for(indices, collection, math.ceil(n/k))
    scores = sharpness_for(indices, collection)
    s = scores.argsort()[::-1]
    best = [np.nonzero(cluster[s]==i)[0][0] for i in range(np.unique(cluster).size)]
    best_idx = indices[s[best]].ravel()
    top_img.extend([int(i) for i in best_idx])

  return top_img

  # top_scores_idx = [scores.argsort()[-math.ceil(n/k):][::-1] for scores in img_scores]
  # top_scores_idx = [scores.argsort()[::-1] for scores in img_sharpness]
  # top_indices = [img_indices[i][top_scores_idx[i]].flatten() for i in range(len(top_scores_idx))]
  # indices = [i for indices in top_indices for i in indices]
  # top_images = [collection(i) for i in indices for indices in top_indices]
  


def get_images(folder):
  def get(n):
    return Image.open(os.path.join(folder, "%05d.jpg" % n))
  return get


def save_images(output, collection):
  try:
    os.makedirs(output)
  except FileExistsError: pass
  def save(i):
    collection(i).save(os.path.join(args.output, "%05d.jpg" % i))
  return save


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("folder")
  parser.add_argument("features")
  parser.add_argument("output")
  parser.add_argument("--n", default=20, type=int)
  parser.add_argument("--k", default=5, type=int)
  args = parser.parse_args()
  collection = get_images(args.folder)
  save = save_images(args.output, collection)
  top_frames = get_top_frames(np.load(args.features), collection, args.n, args.k)
  [save(i) for i in top_frames]
  with open(os.path.join(args.output, "indices.json"), 'w') as fp:
    json.dump(top_frames, fp)
