import argparse
import json
import math
import numpy as np
from PIL import Image
from pprint import pprint
import matplotlib.pyplot as pl

from fgo16 import inference
from fgo16 import input_data
from fgo16 import imageops


parser = argparse.ArgumentParser()
parser.add_argument('image')
parser.add_argument('--gpu', default=1, type=int)
parser.add_argument('--force', default=False, action='store_true')
parser.add_argument('--weights')
parser.add_argument('--synsets')
args = parser.parse_args()

image = Image.open(args.image)
# image = imageops.resize_square(image, 224)
image = imageops.resize(image, 384)
h, w, c = image.shape

classes = input_data.load_classes(args.synsets)

classifier = inference.Classifier(args.weights, (w,h), len(classes), args.gpu)
y = classifier.run([image])

# print(y)
# top = np.argmax(y)
# print(classes[top])


# print(y.shape)
# print(np.argsort(y.sum(axis=1).sum(axis=1)))

im = np.argmax(y, axis=-1)
pl.matshow(np.squeeze(im))
pl.show()

# logits = np.squeeze(logits)
# preds = np.argmax(logits, axis=-1)
# preds, _ = np.histogram(preds, bins=61, range=(0,60))

# synset = json.load(open("fgo_synsets_ids.json"))
# pprint(input_data.get_top_labels(y[0], synset, top=5))
