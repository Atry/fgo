import argparse
import tensorflow as tf
import numpy as np
from pprint import pprint

from fgo16 import fgo
from fgo16 import input_data


class Classifier:
  def __init__(self, weights, input_size, n_classes, gpu):
    self.model, self.session = self.setup(weights, gpu, input_size, n_classes)


  def run(self, images):
    images = [np.array(im) for im in images]
    images = np.concatenate([im[np.newaxis] for im in images], axis=0)
    feed_dict = self.model.no_dropouts()
    feed_dict.update({self.model.images_op: images})
    with self.session.as_default():
      return self.session.run(self.model.prob_op, feed_dict=feed_dict)


  def setup(self, saved, use_gpu, input_size, n_classes):
    model = fgo.FGO(fgo.DefaultWeights(), n_classes, input_size, full_conv=True)
    saver = tf.train.Saver()

    if not use_gpu:
      config = tf.ConfigProto(device_count={'GPU': 0})
    else:
      config = tf.ConfigProto()

    sess = tf.Session(config=config)
    with sess.as_default():
      tf.initialize_all_variables().run()
      saver.restore(sess, saved)

    return model, sess
