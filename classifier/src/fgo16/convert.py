import tensorflow as tf


with open("vgg16.tfmodel", mode='rb') as f:
  fileContent = f.read()

graph_def = tf.GraphDef()
graph_def.ParseFromString(fileContent)

images = tf.placeholder("float", [None, 224, 224, 3])

tf.import_graph_def(graph_def, input_map={ "images": images })

graph = tf.get_default_graph()

with tf.Session() as sess:
  init = tf.initialize_all_variables()
  saver = tf.train.Saver()
  sess.run(init)
  saver.save(sess, "vgg16-model")

