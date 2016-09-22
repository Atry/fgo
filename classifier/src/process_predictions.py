import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
from scipy import misc, signal, ndimage
import os.path

import video
from fgo16 import input_data


def read_metadata(fname):
  with open(fname) as fp:
    return json.load(fp)


def read_labels(fname):
  return input_data.load_classes(fname)
  # with open(fname) as fp:
  #   return json.load(fp)


def timecode_to_seconds(tc, fps):
  hours, minutes, seconds, frames = [int(s) for s in tc.split('_')]
  return hours * 3600 + minutes * 60 + seconds + frames/fps


def get_filenames(base_dir, keyfunc):
  filenames = os.listdir(base_dir)
  filenames = sorted(filenames, key=keyfunc)
  return [os.path.join(base_dir, f) for f in filenames]


def draw_labels(im, f):
  draw = ImageDraw.Draw(im)
  font = ImageFont.truetype(font='DejaVuSans.ttf', size=36)
  [draw.text((x,y), l.split(',')[0].capitalize(), fill=255, font=font) for x,y,l in f]
  del draw
  return im


def extract_max(predictions, meta, labels):
  N, H, W, C = predictions.shape
  W_orig, H_orig = meta['original_size']
  W_scale, H_scale = W/W_orig, H/H_orig
  all_regions = predictions.argmax(axis=3)
  X, Y = np.meshgrid(range(W), range(H))

  def get_uniques(regions):
    return np.unique(regions, return_inverse=True, return_counts=True)

  def get_coordinates(classes, indices):
    c = []
    for i,cl in enumerate(classes):
      coord_indices = indices == i
      x, y = X.flat[coord_indices], Y.flat[coord_indices]
      c.append(np.vstack([x, y]))
    return c

  def means(coord_list):
    return np.vstack([np.median(c, axis=1) for c in coord_list]).T

  def scaled(coords):
    return np.vstack([coords[0]/W_scale, coords[1]/H_scale])

  classes, indices, counts = zip(*[get_uniques(regions) for regions in all_regions])
  argsort = [np.argsort(c)[::-1][:2] for c in counts]
  coordinates = [get_coordinates(u,i) for u,i in zip(classes, indices)]
  mean_coordinates = [means(coords) for coords in coordinates]
  scaled_coordinates = [scaled(c) for c in mean_coordinates]
  encoded = [[(xy[0,i], xy[1,i], c[i])
             for i in s]
             for xy, c, s in zip(scaled_coordinates, classes, argsort)]

  with_labels = [[(x, y, labels[str(c)]) for x,y,c in coords] for coords in encoded]
  return with_labels


def extract_all(predictions, meta, labels):
  MAX = 2
  N, H, W, C = predictions.shape
  X, Y = np.meshgrid(range(W), range(H))

  predictions = np.rollaxis(predictions, 3, 1)
  predictions = np.reshape(predictions, [N, C, H*W])
  pred_sum = np.sum(predictions, 2)
  assert(pred_sum.shape == (N, C))

  weights = predictions / np.tile(pred_sum[..., np.newaxis], [1, 1, H*W])
  Xs = np.tile(X.ravel()[np.newaxis,np.newaxis], [N, C, 1])
  Ys = np.tile(Y.ravel()[np.newaxis,np.newaxis], [N, C, 1])
  Xs_avg = np.average(Xs, 2, weights)
  Ys_avg = np.average(Ys, 2, weights)
  coords = np.dstack([Xs_avg, Ys_avg])
  assert(coords.shape == (N, C, 2))

  filt = signal.gaussian(20, 4.0)
  filt /= filt.sum()
  coords = ndimage.filters.convolve1d(coords, filt, axis=0)

  W_orig, H_orig = meta['original_size']
  W_scale, H_scale = W/W_orig, H/H_orig
  top = np.argsort(pred_sum, axis=1)[...,-MAX:]
  print(top[:100])
  top_coords = np.vstack([coords[i,top[i],:][np.newaxis,...] for i in range(N)])
  loc = np.dstack([top_coords, top])
  loc[...,0] /= W_scale
  loc[...,1] /= H_scale
  assert(loc.shape == (N, MAX, 3))

  with_labels = [[(loc[i,j,0], loc[i,j,1], labels[int(loc[i,j,2])])
                  for j in range(MAX)]
                 for i in range(N)]
  return with_labels


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('metadata')
  parser.add_argument('predictions')
  parser.add_argument('labels')
  # parser.add_argument('video')
  parser.add_argument('output')
  args = parser.parse_args()

  meta = read_metadata(args.metadata)
  labels = read_labels(args.labels)
  keyfunc = lambda s: timecode_to_seconds('.'.join(s.split('.')[:-1]), meta['true_fps'])
  filenames = get_filenames(args.predictions, keyfunc)
  predictions = np.stack([np.load(f) for f in filenames])

  # plt.matshow(predictions[0].argmax(axis=2))
  # plt.show()
  # return

  W_orig, H_orig = meta['original_size']

  # with_labels = extract_max(predictions, meta, labels)
  with_labels = extract_all(predictions, meta, labels)

  def frames_generator():
    for i,f in enumerate(with_labels):
        blank = Image.new('L', (W_orig, H_orig))
        yield draw_labels(blank, f)

  video.images_to_video(frames_generator(), args.output, meta['sampled_fps'], meta['true_fps'])


main()
