import os.path
import tensorflow as tf


class Optimizer:

  def setup_summary(self, logdir):
    if logdir:
      path = os.path.join(param.logdir, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
      return tf.train.SummaryWriter(logdir, graph_def=self.session.graph_def, flush_secs=30)
    else:
      return None


  def __init__(self, session, model, learning_rate, logdir=None):
    self.session = session
    self.model = model
    self.lr = learning_rate
    self.summary_writer = self.setup_summary(logdir)
    self.accuracies = []

    with tf.name_scope("train"):
      self.global_step = tf.Variable(0, name="global_step", trainable=False)
      self.lr_op = tf.Variable(self.lr, name="learning_rate", trainable=False)
      self.loss_op = self.model.cost(self.model.logits_op, self.model.labels_op)
      self.summary_op = self.summaries()
      optimizer = tf.train.AdagradOptimizer(self.lr_op)
      # optimizer = tf.train.MomentumOptimizer(self.lr_op, 0.001)
      self.optimizer = optimizer.minimize(self.loss_op, global_step=self.global_step)


  def train_step(self, image_batch, label_batch):
    feed_dict = {
      self.model.images_op: image_batch,
      self.model.labels_op: label_batch,
      self.lr_op: self.lr
    }
    self.train, loss, self.step, summary, accuracy = self.session.run([
      self.optimizer,
      self.loss_op,
      self.global_step,
      self.summary_op,
      self.model.accuracy_op
    ], feed_dict=feed_dict)
    return loss, accuracy


  def accuracy_once(self, batch):
    image_batch, label_batch = batch
    feed_dict = self.model.feed_accuracy(image_batch, label_batch)
    return self.session.run([self.model.accuracy_op, self.loss_op], feed_dict=feed_dict)


  def compute_accuracy(self, batches):
    correct = 0.0
    total = 0.0
    for batch in batches:
      acc, loss = self.accuracy_once(batch)
      correct += acc
      total += batch[0].shape[0]
    accuracy = correct/total
    self.accuracies.append(accuracy)
    return accuracy


  def summaries(self):
    tf.image_summary(self.model.images_op.op.name, self.model.images_op)
    tf.scalar_summary(self.loss_op.op.name, self.loss_op)
    # tf.scalar_summary(accuracy.op.name, accuracy)
    return tf.merge_all_summaries()


  def adaptLearningRate(self):
    if (len(self.accuracies) > 2
        and self.accuracies[-1] <= self.accuracies[-3]
        and self.accuracies[-2] <= self.accuracies[-3]):
      self.lr /= 10.0
      print("new learning rate: %f" % self.lr)
