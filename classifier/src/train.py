import argparse
import datetime
import os
import os.path
import skimage
from pprint import pprint
import tensorflow as tf
import sys
import random
import numpy as np

from fgo16 import fgo
from fgo16 import input_data
from fgo16.optimizer import Optimizer


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('data')
  parser.add_argument('synsets')
  parser.add_argument('saved')
  parser.add_argument('--lr', default=1e-2, type=float)
  parser.add_argument('--gpu', default=1, type=bool)
  parser.add_argument('--save', default=None)
  parser.add_argument('--logdir', default=None)
  parser.add_argument('--steps', default=None, type=int)
  parser.add_argument('--steps_save', default=100, type=int)
  parser.add_argument('--steps_eval', default=50, type=int)
  parser.add_argument('--batch_size', default=64, type=int)
  parser.add_argument('--eval_size', default=0, type=int)
  args = parser.parse_args()

  wnids = input_data.load_wnids(args.synsets)
  files_classes = input_data.join_images(args.data, wnids)
  # pprint(input_data.load_classes(args.synsets))

  train_set, validation_set, test_set = input_data.splits(files_classes)
  print("Train set (%d), validation set (%d), test set (%d)" %
        (len(train_set), len(validation_set), len(test_set)))
  train_batches = input_data.load_batches(train_set, args.batch_size, finite=False, shuffle=True, randflip=True, randshift=True, randcrop=True)

  if args.eval_size > 0:
    validation_set = validation_set[:args.eval_size]


  def computeEpoch(step):
    return (step*args.batch_size)/len(train_set)


  default_data = fgo.DefaultWeights()
  model = fgo.FGO(default_data, len(wnids))

  saver = tf.train.Saver()

  def eval_accuracy(optimizer, file_set):
    print("Computing accuracy...")
    batches = input_data.load_batches(file_set, args.batch_size, finite=True, shuffle=False, randflip=False, randshift=False, randcrop=False)
    accuracy = optimizer.compute_accuracy(batches)
    print("Accuracy on validation set: %.3f%%" % (100*accuracy))


  if not args.gpu:
    config = tf.ConfigProto(device_count={'GPU': 0})
  else:
    config = tf.ConfigProto()

  with tf.Session(config=config) as sess:

    optimizer = Optimizer(sess, model, args.lr, args.logdir)
    tf.initialize_all_variables().run()
    saver.restore(sess, args.saved)

    eval_accuracy(optimizer, validation_set[:256])

    for image_batch, label_batch in train_batches:
      loss, accuracy = optimizer.train_step(image_batch, label_batch)
      print("%d (%.2f) %.1f (%.2f)" %
            (optimizer.step, computeEpoch(optimizer.step), loss, accuracy/args.batch_size))

      if optimizer.step % args.steps_eval == 0:
        eval_accuracy(optimizer, validation_set)
        optimizer.adaptLearningRate()

      if args.save and optimizer.step % args.steps_save == 0:
        path = saver.save(sess, args.save, global_step=optimizer.step)
        print("Saved model to %s" % path)

      if args.steps and optimizer.step >= args.steps:
        print("Reached (%d/%d) steps, stopping..." % (step, args.steps))
        break
