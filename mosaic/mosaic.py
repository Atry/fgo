import argparse
import sys
import json
import random
import numpy as np
import skimage
from skimage import io, transform, color
from pprint import pprint
import math


var = 0.3

def get_splits(n, mean, var):
    return [(i*mean + var*(random.random()-0.5)) for i in range(1,n)]


def neighbour(a):
    def func(el):
        i, b = el
        dx = b[0]-a[0]
        dy = b[1]-a[1]
        return abs(dx) <= 1 and dy == 0 or abs(dy) <= 1 and dx == 0
    return func


def neighbour2(x):
    def func(el):
        a = x
        i, b = el
        if a.shape[0] < b.shape[0]: a,b = b,a
        ca = a.sum(0) / a.shape[0]
        if b.shape[0] == 2:
            cb = b.sum(0) / b.shape[0]
            d = np.linalg.norm(ca - cb)
            return d == 1
        elif b.shape[0] == 1:
            d = np.linalg.norm(ca - b[0,:])
            return d == 1.5
    return func


def get_coord(w_splits, h_splits):
    def func(cell):
        tl = cell.min(0)
        br = cell.max(0)
        return {
            'tx1': 0.0 if tl[0]==0 else w_splits[tl[0]-1],
            'ty1': 0.0 if tl[1]==0 else h_splits[tl[1]-1],
            'tx2': 1.0 if br[0]>=len(w_splits) else w_splits[br[0]],
            'ty2': 1.0 if br[1]>=len(h_splits) else h_splits[br[1]]
        }
        # return np.array([tx1, ty1, tx2, ty2])
    return func



# aspect_ratio = w/h
def mondrian_tiles(aspect_ratio, n_tiles):
    sqrt = math.sqrt(n_tiles)
    n_width = int(math.ceil(sqrt * aspect_ratio))
    n_height = int(math.ceil(sqrt))
    if random.random() >= 0.5:
        n_width, n_height = n_height, n_width
    mean_width = 1.0 / n_width
    mean_height = 1.0 / n_height

    w_splits = get_splits(n_width, mean_width, mean_width*var)
    h_splits = get_splits(n_height, mean_height, mean_height*var)

    coords = [np.array([x,y]) for x in range(n_width) for y in range(n_height)]
    cells2 = []
    while len(coords):
        a = coords.pop(random.randint(0,len(coords)-1))
        neighbours = list(filter(neighbour(a), enumerate(coords)))
        if len(neighbours) and len(coords)+len(cells2)+1 > n_tiles:
            chosen = random.choice(neighbours)
            b = coords.pop(chosen[0])
            cells2.append(np.array([a,b]))
        else:
            cells2.append(np.array([a]))

    cells = []
    while len(cells2):
        a = cells2.pop(random.randint(0,len(cells2)-1))
        neighbours = list(filter(neighbour2(a), enumerate(cells2)))
        if len(neighbours) and len(cells)+len(cells2)+1 > n_tiles:
            bi, _ = random.choice(neighbours)
            cells.append(np.vstack((a, cells2.pop(bi))))
        else:
            cells.append(a)
    
    return list(map(add_blanks(0.005), map(get_coord(w_splits, h_splits), cells)))


def crop(aspect_ratio, img, tile):
    w = tile['tx2']-tile['tx1']
    h = tile['ty2']-tile['ty1']
    ar_tile = aspect_ratio*w/float(h)
    ar_img = img.shape[1]/float(img.shape[0])
    c = {
        'cx1': 0.0,
        'cy1': 0.0,
        'cx2': 1.0 if ar_tile >= ar_img else ar_tile/ar_img,
        'cy2': 1.0 if ar_tile < ar_img else ar_img/ar_tile
    }
    # if ar_tile >= ar_img:
    #     d = 0.5 - (c['cy2'] + c['cy1'])/2.0
    #     c['cy1'] += d
    #     c['cy2'] += d
    # else:
    #     d = 0.5 - (c['cx2'] + c['cx1'])/2.0
    #     c['cx1'] += d
    #     c['cx2'] += d
    return c
    

def to_json(f, crop, tile):
    crop.update({'imfile': f, 'rot': 0})
    crop.update(tile)
    return crop


def add_blanks(m):
    def func(t):
        t['tx1'] += m if t['tx1'] == 0 else m/2.0
        t['ty1'] += m if t['ty1'] == 0 else m/2.0
        t['tx2'] -= m if t['tx2'] == 1 else m/2.0
        t['ty2'] -= m if t['ty2'] == 1 else m/2.0
        return t
    return func


def saliency_center(im):
    pass
    # facecascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # gray = skimage.img_as_ubyte(color.rgb2gray(im))
    # faces = facecascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30,30))
    # print(faces)


def make_mosaic(images, crops, tiles, aspect_ratio, width):
    height = width/aspect_ratio
    mosaic = np.ones([height, width, 3])
    tiles = [(math.floor(t['tx1']*width), math.floor(t['tx2']*width), math.floor(t['ty1']*height), math.floor(t['ty2']*height))
     for t in tiles]

    for im, c, t in zip(images, crops, tiles):
      tx1, tx2, ty1, ty2 = t
      tw, th = tx2-tx1, ty2-ty1
      h, w = im.shape[:2]
      cx1, cx2, cy1, cy2 = round(c['cx1']*w), round(c['cx2']*w), round(c['cy1']*h), round(c['cy2']*h)
      s = saliency_center(im)
      im = im[cy1:cy2, cx1:cx2]
      im = transform.rescale(im, max(th/float(im.shape[0]), tw/float(im.shape[1])))
      im = im[:th,:tw]
      mosaic[ty1:ty2, tx1:tx2] = im

    return mosaic


def fill_tiles(imfiles, tiles, aspect_ratio):
    indices = range(len(imfiles))
    imgs = [io.imread(imfiles[i]) for i in indices]
    crops = [crop(aspect_ratio, im, t) for im, t in zip(imgs, tiles)]
    m = make_mosaic(imgs, crops, tiles, aspect_ratio, 2048)
    return m
    # return list(map(to_json, imfiles, crops, tiles))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("imfiles", nargs='+')
    parser.add_argument("out")
    parser.add_argument("--ar", default=math.sqrt(2), type=float)
    args = parser.parse_args()
    # ar = float(sys.argv[1])
    # imfiles = sys.argv[2:-1]
    # out = sys.argv[-1]
    tiles = mondrian_tiles(args.ar, len(args.imfiles))
    d = fill_tiles(args.imfiles, tiles, args.ar)
    if args.out is '-':
        io.imshow(d)
        io.show()
    else:
        io.imsave(args.out, d)
