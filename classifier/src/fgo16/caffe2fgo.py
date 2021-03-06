import argparse
import os
os.environ["GLOG_minloglevel"] = "2"

import os.path
import skimage
import caffe
import numpy as np
import math
import tensorflow as tf

import fgo
import input_data


class CaffeData(fgo.DefaultWeights):
  def __init__(self, prototxt, caffemodel):
    net_caffe = caffe.Net(prototxt, caffemodel, caffe.TEST)
    self.caffe_layers = {}
    for i, layer in enumerate(net_caffe.layers):
      layer_name = net_caffe._layer_names[i]
      self.caffe_layers[layer_name] = layer


  def caffe_weights(self, layer_name):
    layer = self.caffe_layers[layer_name]
    return layer.blobs[0].data


  def caffe_bias(self, layer_name):
    layer = self.caffe_layers[layer_name]
    return layer.blobs[1].data

    # converts caffe filter to tf
    # tensorflow uses [filter_height, filter_width, in_channels, out_channels]
    #                  2               3            1            0
    # need to transpose channel axis in the weights
    # caffe:  a convolution layer with 96 filters of 11 x 11 spatial dimension
    # and 3 inputs the blob is 96 x 3 x 11 x 11
    # caffe uses [out_channels, in_channels, filter_height, filter_width] 
    #             0             1            2              3
  def caffe2tf_filter(self, name):
    f = self.caffe_weights(name)
    return f.transpose((2, 3, 1, 0))


    # caffe blobs are [ channel, height, width ]
    # this returns  [ height, width, channel ]
  def caffe2tf_conv_blob(self, name):
    blob = net_caffe.blobs[name].data[0]
    return blob.transpose((1, 2, 0))


  def caffe2tf_1d_blob(self, name):
    blob = net_caffe.blobs[name].data[0]
    return blob


  def get_conv_bias(self, name):
    b = self.caffe_bias(name)
    return np.array(b, dtype=np.float32)


  def get_conv_filter(self, name):
    w = self.caffe2tf_filter(name)
    return np.array(w, dtype=np.float32)


  def get_fc_weights(self, name):
    if name == "fc8":
      return None
    cw = self.caffe_weights(name)
    if name == "fc6":
      assert cw.shape == (4096, 25088)
      cw = cw.reshape((4096, 512, 7, 7))
      cw = cw.transpose((2, 3, 1, 0))
      cw = cw.reshape(25088, 4096)
    else:
      cw = cw.transpose((1, 0))
    return np.array(cw, dtype=np.float32)


  def get_fc_bias(self, name):
    if name == "fc8":
      return None
    b = self.caffe_bias(name)
    return np.array(b, dtype=np.float32)


  # def get_fc_weight_mod(self, name, shape, trainable, decay=None):
  #   cw = caffe_weights(name).transpose((1,0))
  #   indices, known = input_data.get_indices()
  #   W = np.array(np.random.randn(cw.shape[0], len(indices)), dtype=np.float32) * 1e-2
  #   for i in known:
  #     W[:, i] = cw[:, indices[i]]
  #   t = tf.Variable(W, name="weight")
  #   return t

  # def get_bias_mod(self, name, shape, trainable):
  #   b = caffe_bias(name)
  #   indices, known = input_data.get_indices()
  #   B = np.array(np.zeros((len(indices),)), dtype=np.float32)
  #   B[known] = b[indices[known]]
  #   t = tf.Variable(B, name="bias")
  #   return t


# def model(X, y):
#   prediction, loss = ModelFromCaffe().build(X, y, train=False)
#   return prediction, loss


# def main_skflow():
#   classifier = fgo.FGOEstimator(model_fn=model, n_classes=61, steps=0)
#   classifier.fit(np.ones([1, 224, 224, 3], dtype=np.float32), np.ones([1,], dtype=np.float32))
#   classifier.save_variables("fgo16-skflow")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("prototxt")
  parser.add_argument("caffemodel")
  parser.add_argument("output")
  args = parser.parse_args()

  default_data = CaffeData(args.prototxt, args.caffemodel)
  model = fgo.FGO(default_data, 25)

  init = tf.initialize_all_variables()
  saver = tf.train.Saver()
  with tf.Session() as sess:
    sess.run(init)
    path = saver.save(sess, args.output)
    print("saved variables to %s" % path)
