import numpy as np
import random
import skimage
from skimage import io, transform


def crop(img, randomize=False):
  # img = img / 255.0
  short_edge = min(img.shape[:2])
  if randomize:
    yy = random.randint(0, img.shape[0] - short_edge)
    xx = random.randint(0, img.shape[1] - short_edge)
  else:
    yy = int((img.shape[0] - short_edge) / 2)
    xx = int((img.shape[1] - short_edge) / 2)
  crop_img = img[yy : yy + short_edge, xx : xx + short_edge]
  resized_img = transform.resize(crop_img, (224, 224))
  return resized_img * 255 # because resizing converts to float [0,1]


def random_flip(im):
  if random.random() >= 0.5:
    flipped = np.fliplr(im)
    if len(im.shape) == 3:
      assert flipped[0,3,0] == im[0,-4,0]
    else:
      assert flipped[0,3] == im[0,-4]
    return flipped
  return im


def random_shift(im):
  # if random.random() >= 0.5:
  #   return im
  return im


def preprocess(image):
  return crop(np.array(image))


def compute_size(shape, s=384):
  w, h = shape
  ar = w / h
  if ar > 1:
    return (round(s*ar), s)
  else:
    return (s, round(s/ar))


def resize(image, size):
  new_size = compute_size(image.size, size)
  image = image.resize(new_size)
  return np.array(image)


def resize_square(image, size):
  return np.array(image.resize((size,size)))


def get_load_image(randflip=False, randshift=False, randcrop=False):
  def load(path):
    img = io.imread(path)
    img = crop(img, randcrop)
    if randflip: img = random_flip(img)
    # if randshift: img = random_shift(img)
    return img
  return load


def getImageCollection(paths, loadOpts):
  randflip, randshift, randcrop = loadOpts
  return io.ImageCollection(paths, load_func=get_load_image(randflip, randshift, randcrop))
