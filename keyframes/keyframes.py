import sys
import numpy
import scipy
from scipy import ndimage
from scipy import signal
from PIL import Image
from matplotlib import pyplot as pl


def extract_histogram(image):
    return numpy.concatenate([ndimage.measurements.histogram(image[:,:,c], 0, 255, 10) for c in range(image.shape[2])])


def plot_gradients(g):
    pl.plot(g)
    pl.show()


def split_shots(histograms):
    gradients = (numpy.diff(histograms)**2).sum(0)
    plot_gradients(gradients)
    peaks_idx = signal.argrelmax(gradients, order=10)
    return numpy.split(numpy.arange(histograms.shape[1]), peaks_idx[0])


def match_shots(shots):
    pass


def find_middle_keyframe(shot):
    return int(shot.size / 2)


def find_keyframes(scenes):
    return list(map(find_middle_keyframe, scenes))


def main(filenames):
    frames_img = list(map(Image.open, filenames))
    frames = map(numpy.array, frames_img)
    histograms = map(extract_histogram, frames)
    histograms_vec = numpy.array(list(histograms)).T
    shots_idx = split_shots(histograms_vec)
    # scenes = match_shots(shots)
    keyframes_idx = find_keyframes(shots_idx)
    keyshots_idx = [shots_idx[n][i] for n,i in zip(range(len(shots_idx)),keyframes_idx)]
    keyframes = [frames_img[i] for i in keyshots_idx]
    keyframes_names = map(lambda x: "keyframes/{}.jpg".format(x), range(len(keyframes)))
    # map(lambda f,x: x.save(f), keyframes_names, keyframes)
    for f,x in zip(keyframes_names, keyframes):
        x.save(f)


if __name__ == '__main__':
    main(sys.argv[1:])
