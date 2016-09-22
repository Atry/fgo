import argparse
import datetime
import json
import math
import numpy as np
import os
import os.path
from queue import Empty
import sys

from fgo16 import imageops
from fgo16 import inference
from fgo16 import input_data
import video


def save_frames(name, fps):
  path = os.path.join(name, "frames", "%dfps" % fps)
  try:
    os.makedirs(path)
  except OSError: pass

  def save(image, frame_no):
    image.save(os.path.join(path, "%05d.jpg" % frame_no))
  return save


def log(nframes):
  def hook(i):
    sys.stdout.write("\rpredictions up to frame %05d (%.2f%%)" % (i, 100.0*i/nframes))
    sys.stdout.flush()
  return hook


def save_results(outname, fps, true_fps):
  try:
    os.makedirs(outname)
  except OSError: pass

  def func(batch_frames, array):
    for i, frame in enumerate(batch_frames):
      timecode = video.compute_timecode(fps, true_fps, frame)
      fname = "_".join(["%02d" % x for x in timecode])
      np.save(os.path.join(outname, fname), array[i])
  return func


def run_classifier_on_queue(queue, classifier, batch_size, log_hook, save_results_hook):
  try:
    images = []
    batch_indices = []
    i = 0
    while True:
      try:
        image = queue.get(timeout=30)
        image = imageops.resize(image, 384)
        images.append(image)
        batch_indices.append(i)
      except Empty:
        print("decoded all video frames")
        break

      if len(images) >= batch_size:
        log_hook(i)
        predictions = classifier.run(images)
        images = []
        save_results_hook(batch_indices, predictions)
        batch_indices = []
      i += 1
  except KeyboardInterrupt:
    pass


def save_metadata(fname, info, args, target_size):
    with open(fname, 'w') as fp:
      json.dump({
        'true_fps': info['fps'],
        'sampled_fps': args.fps,
        'gpu_used': args.gpu,
        'weights_used': args.weights,
        'batch_size': args.batch,
        'original_size': info['size'],
        'evaluated_size': target_size,
        'duration': video.compute_seconds(info['duration']),
        'date': str(datetime.datetime.today())
      }, fp, indent=2)


def get_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('video')
  parser.add_argument('output_folder')
  parser.add_argument('--fps', default=0, type=int)
  parser.add_argument('--batch', default=2, type=int)
  parser.add_argument('--gpu', default=0, type=int)
  parser.add_argument('--force', default=False, action='store_true')
  parser.add_argument('--weights')
  return parser.parse_args()


if __name__ == '__main__':
  args = get_arguments()

  videoname = args.video.split("/")[-1]
  outname = os.path.join(args.output_folder, ".".join(videoname.split(".")[:-1]))
  try:
    os.makedirs(outname)
  except OSError:
    if args.force:
      print("Output folder [%s] already exists, overwriting,..." % outname)
    else:
      print("Output folder [%s] cannot be created, or already exists" % outname)
      sys.exit(1)

  info = video.video_info(args.video)
  if args.fps == 0:
    args.fps = info['fps']

  target_size = imageops.compute_size(info['size'], 384)
  save_metadata(os.path.join(outname, "metadata.json"), info, args, target_size)
  nframes = video.compute_nframes(info['duration'], args.fps)
  classifier = inference.Classifier(args.weights, target_size, 25, args.gpu)

  log_hook = log(nframes)
  save_results_hook = save_results(os.path.join(outname, "predictions"), args.fps, info['fps'])

  print("decoding video: %s\n\tsize: %s\n\tframes: %d" % (args.video, info['size'], nframes))
  queue, thread = video.decode_video_to_queue(args.video, info['size'], args.fps)
  thread.start()
  run_classifier_on_queue(queue, classifier, args.batch, log_hook, save_results_hook)
