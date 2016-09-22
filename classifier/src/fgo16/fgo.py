import math
import tensorflow as tf


class DefaultWeights:
  def __init__(self):
    pass

  def get_conv_bias(self, name):
    return None

  def get_conv_filter(self, name):
    return None

  def get_fc_weights(self, name):
    return None

  def get_fc_bias(self, name):
    return None


def get_variable(name, default, shape, trainable):
  if default is not None:
    var = tf.Variable(default, name=name)
  else:
    var = tf.get_variable(name, shape, initializer=tf.uniform_unit_scaling_initializer(), trainable=trainable)
  return var


def max_pool(bottom, name):
  return tf.nn.max_pool(bottom, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
    padding='SAME', name=name)


class Model:
  DROPOUTS = "dropouts"
  LOSSES = "losses"

  def conv2d(self, bottom, name, shape_f, shape_out, trainable):
    fh, fw = shape_f
    n_channels = bottom.get_shape()[-1].value
    shape_w = (fh, fw, n_channels, shape_out)

    with tf.variable_scope(name) as scope:
      filt = get_variable("filter", self.loader.get_conv_filter(name), shape_w, trainable)
      bias = get_variable("bias", self.loader.get_conv_bias(name), (shape_out,), trainable)
      conv = tf.nn.conv2d(bottom, filt, [1, 1, 1, 1], padding='SAME')
      biased = tf.nn.bias_add(conv, bias)
      return tf.nn.relu(biased)


  def flattened_shape(self, tensor):
    shape = tensor.get_shape().as_list()
    dim = 1
    for d in shape[1:]:
        dim *= d
    return dim


  def fc_weights_biases(self, name, shape_in, shape_out, trainable):
    shape_w = (shape_in, shape_out)
    weights = get_variable("weight", self.loader.get_fc_weights(name), shape_w, trainable)
    bias = get_variable("bias", self.loader.get_fc_bias(name), (shape_out,), trainable)
    return weights, bias


  def fc(self, bottom, name, shape_out, trainable, weight_decay):
    print(name, bottom.get_shape())
    dim = self.flattened_shape(bottom)
    x = tf.reshape(bottom, [-1, dim])
    with tf.variable_scope(name):
      weights, bias = self.fc_weights_biases(name, dim, shape_out, trainable)
      weights = self.with_decay(weights, weight_decay)
      out = tf.nn.bias_add(tf.matmul(x, weights), bias)
      return tf.nn.relu(out)


  def fc2conv(self, bottom, name, shape_in, shape_f, shape_out):
    with tf.variable_scope(name):
      weights, biases = self.fc_weights_biases(name, shape_in, shape_out, False)
      fh, fw = shape_f
      n_channels = bottom.get_shape()[-1].value
      filters = tf.reshape(weights, [fh, fw, n_channels, shape_out])
      conv = tf.nn.bias_add(tf.nn.conv2d(bottom, filters, [1,1,1,1], padding='VALID'), biases)
      return tf.nn.relu(conv)


  def with_decay(self, var, wd):
      weight_decay = tf.mul(tf.nn.l2_loss(var), wd, name="weight_loss")
      tf.add_to_collection(self.LOSSES, weight_decay)
      return var


  def with_dropout(self, var, name, prob):
    with tf.variable_scope(name):
      drop = tf.get_variable("dropout", [], initializer=tf.constant_initializer(prob), trainable=False)
      tf.add_to_collection(self.DROPOUTS, drop)
      return tf.nn.dropout(var, drop)


  def no_dropouts(self):
    dropouts = tf.get_collection(self.DROPOUTS)
    return {drop: 1.0 for drop in dropouts}



class FGO(Model):
  VGG_MEAN = [103.939, 116.779, 123.68]

  def __init__(self, loader, n_classes, imsize=(224,224), full_conv=False):
    self.loader = loader
    self.images_op, self.labels_op = self.inputs(imsize)
    self.logits_op = self.graph(self.images_op, n_classes, 5e-4, full_conv)
    self.prob_op = self.inference(self.logits_op)
    if not full_conv:
      self.accuracy_op = self.accuracy(self.prob_op, self.labels_op)


  def graph(self, rgb, n_classes, wd, full_conv):
    red, green, blue = tf.split(3, 3, rgb)
    bgr = tf.concat(3, [
      blue - self.VGG_MEAN[0],
      green - self.VGG_MEAN[1],
      red - self.VGG_MEAN[2],
    ])

    relu1_1 = self.conv2d(bgr, "conv1_1", (3,3), 64, False)
    relu1_2 = self.conv2d(relu1_1, "conv1_2", (3,3), 64, False)
    pool1 = max_pool(relu1_2, 'pool')

    relu2_1 = self.conv2d(pool1, "conv2_1", (3,3), 128, False)
    relu2_2 = self.conv2d(relu2_1, "conv2_2", (3,3), 128, False)
    pool2 = max_pool(relu2_2, 'pool')

    relu3_1 = self.conv2d(pool2, "conv3_1", (3,3), 256, False)
    relu3_2 = self.conv2d(relu3_1, "conv3_2", (3,3), 256, False)
    relu3_3 = self.conv2d(relu3_2, "conv3_3", (3,3), 256, False)
    pool3 = max_pool(relu3_3, 'pool')

    relu4_1 = self.conv2d(pool3, "conv4_1", (3,3), 512, False)
    relu4_2 = self.conv2d(relu4_1, "conv4_2", (3,3), 512, False)
    relu4_3 = self.conv2d(relu4_2, "conv4_3", (3,3), 512, False)
    pool4 = max_pool(relu4_3, 'pool')

    relu5_1 = self.conv2d(pool4, "conv5_1", (3,3), 512, False)
    relu5_2 = self.conv2d(relu5_1, "conv5_2", (3,3), 512, False)
    relu5_3 = self.conv2d(relu5_2, "conv5_3", (3,3), 512, False)
    pool5 = max_pool(relu5_3, 'pool')

    if full_conv:
      relu6 = self.fc2conv(pool5, "fc6", 25088, (7,7), 4096)
      relu7 = self.fc2conv(relu6, "fc7", 4096, (1,1), 4096)
      logits = self.fc2conv(relu7, "fc8", 4096, (1,1), n_classes)
    else:
      relu6 = self.with_dropout(self.fc(pool5, "fc6", 4096, True, wd), "fc6", 0.5)
      relu7 = self.with_dropout(self.fc(relu6, "fc7", 4096, True, wd), "fc7", 0.5)
      logits = self.fc(relu7, "fc8", n_classes, True, wd)

    return logits


  def inference(self, logits):
    shape = logits.get_shape().as_list()
    logits_ = tf.reshape(logits, [-1, shape[-1]])
    sm = tf.nn.softmax(logits_, name="prob")
    if len(shape) > 2: # convolutional
      return tf.reshape(sm, [-1, shape[1], shape[2], shape[3]])
    return sm


  def cost(self, logits, labels):
    n_classes = logits.get_shape()[1].value
    with tf.name_scope("train"):
      cross = tf.nn.sparse_softmax_cross_entropy_with_logits(logits, labels)
      cross_mean = tf.reduce_mean(cross, name="loss")
      tf.add_to_collection(self.LOSSES, cross_mean)
      return tf.add_n(tf.get_collection(self.LOSSES), name="total_loss")


  def accuracy(self, prob, labels):
    with tf.name_scope("test"):
      in_top_k = tf.nn.in_top_k(prob, labels, 1)
      return tf.reduce_sum(tf.cast(in_top_k, tf.float32), name="accuracy")


  def inputs(self, imsize=(224,224)):
    w, h = imsize
    images = tf.placeholder("float", [None, h, w, 3], name="images")
    labels = tf.placeholder(tf.int32, [None], name="labels")
    return images, labels


  def feed_accuracy(self, image_batch, label_batch):
    feed_dict = self.no_dropouts()
    feed_dict.update({self.images_op: image_batch, self.labels_op: label_batch})
    return feed_dict
