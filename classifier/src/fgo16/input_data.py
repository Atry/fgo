import os
import numpy as np
from pprint import pprint
import random

from fgo16 import imageops


def split_list(files, d=0.8):
  split_test = int(d*len(files))
  return files[:split_test], files[split_test:]


def splits(files):
  rest, test_files = split_list(files, 0.9)
  # train_files, validation_files = split_list(rest)
  # return train_files, validation_files, test_files
  return rest, test_files, []


def load_labels(path):
  lines = [l.strip().split() for l in open(path) if not l.startswith("#")]
  return [(l[0], " ".join(l[1:])) for l in lines]


def load_classes(path):
  _, classes = zip(*load_labels(path))
  return classes


def load_wnids(path):
  wnids, _ = zip(*load_labels(path))
  return wnids


def makeFolderList(folder, wnids):
  return filter(lambda p: os.path.exists(p[1]),
                [(i,os.path.join(folder, w))
                 for i,w in enumerate(wnids)])


def join_images(folder, wnids):
  l = [(os.path.join(path, filename), i)
       for i, path in makeFolderList(folder, wnids)
       for filename in os.listdir(path)]
  # random.seed(1)
  random.shuffle(l)
  return l


def load_batches(files, batch_size, finite=True, shuffle=False, randflip=False, randshift=False, randcrop=False):
  paths, class_ids = zip(*files)
  collection = imageops.getImageCollection(paths, (randflip, randshift, randcrop))
  labels = np.array(class_ids)
  processed = 0
  idx = 0
  while not finite or processed < len(files):
    _images = []
    _labels = []
    i = 0
    while i < batch_size:
      if shuffle:
        idx = random.randint(0,len(files)-1)
      else:
        idx = (idx + 1) % len(files)
      try:
        x = collection[idx]
        if x.shape == (224,224,3):
          _images.append(x)
          _labels.append(labels[idx])
          i += 1
      except IOError: pass
    im = np.stack(_images, axis=0)
    lab = np.stack(_labels, axis=0)
    assert im.shape == (batch_size, 224, 224, 3)
    assert lab.shape == (batch_size,)
    yield im, lab
    processed += i
