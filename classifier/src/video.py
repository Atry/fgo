from io import BytesIO
import math
from PIL import Image
from queue import Queue
import re
import subprocess
from threading import Thread


def compute_timecode(fps, true_fps, frames_elapsed):
    second_elapsed = frames_elapsed / fps
    current_second = math.floor(second_elapsed)
    frame = round(true_fps * (second_elapsed - current_second))
    hour = math.floor(second_elapsed / 3600)
    minute = math.floor(second_elapsed / 60) - hour * 60
    second = math.floor(second_elapsed) - minute * 60 - hour * 3600
    return [hour, minute, second, frame]


def get_frame(filename, tc, fps):
  timecode = "%02d:%02d:%02d.%03d" % (tc[0], tc[1], tc[2], tc[3]/fps)
  args = ["ffmpeg",
         "-ss", timecode,
         "-i", filename,
         '-vcodec', 'ppm',
         "-vframes", "1",
         '-loglevel', 'error',
         "-f", "image2pipe", "-"]
  proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  im = read_image(proc.stdout)
  return im


def read_duration(s):
  duration = re.search(r'Duration: (\d+)\:(\d+)\:(\d+)\.(\d+)', s)
  if duration:
    return tuple([int(n) for n in duration.groups()])
  else: raise Exception("No duration found")


def read_size(s):
  size = re.search(r'Video:.*?,.*?, (\d+)x(\d+)', s)
  if size:
    return tuple([int(n) for n in size.groups()])
  else: raise Exception("No size found")


def read_fps(s):
  fps = re.search(r"Video: .*? ([\d\.]+) fps", s)
  if fps:
    return int(fps.group(1))
  else: raise Exception("No fps found")


def compute_seconds(duration):
  return duration[0]*3600 + duration[1]*60 + duration[2] + duration[3]*1e-2


def compute_nframes(duration, fps):
  seconds = compute_seconds(duration)
  return int(math.ceil(seconds * fps))


def video_info(video_fname):
  p = subprocess.Popen(['ffprobe', '-i', video_fname], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
  stdout = p.stdout.read()
  duration = read_duration(stdout)
  size = read_size(stdout)
  fps = read_fps(stdout)
  return {'duration': duration, 'size': size, 'fps': fps}


def read_image(out):
  buf = BytesIO(out)
  return Image.open(buf)


def read_images(out, queue, nbytes):
  while True:
    buf = b''
    for i in range(3):
      buf += out.readline()
    if not len(buf): break
    buf += out.read(nbytes)
    iobuf = BytesIO(buf)
    iobuf.seek(0)
    queue.put(Image.open(iobuf))
  out.close()


def decode_video_to_queue(video_fname, size, fps=5):
  width, height = size
  nbytes = width*height*3
  args = ['ffmpeg',
      '-i', video_fname,
      '-r', str(fps),
      '-f', 'image2pipe',
      '-vcodec', 'ppm',
      '-loglevel', 'error',
      '-']
  proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  queue = Queue(maxsize=50)
  thread = Thread(target=read_images, args=(proc.stdout, queue, nbytes))
  thread.daemon = True
  return queue, thread


def images_to_video(generator, output, sampled_fps, true_fps):
  args = ["ffmpeg",
          "-f", "image2pipe",
          "-vcodec", "png",
          "-r", str(sampled_fps),
          "-i", "-",
          "-vcodec", "mpeg4",
          "-r", str(true_fps),
          output]
  proc = subprocess.Popen(args, stdin=subprocess.PIPE)
  for f in generator:
    f.save(proc.stdin, 'PNG')
  proc.stdin.close()
  proc.wait()
