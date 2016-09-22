# import gevent
import argparse
import grequests
import requests
from pprint import pprint
import os
import os.path
from PIL import Image
from io import BytesIO
import random


def get_synsets_from_wnids(idfile="wnids.txt"):
  WNID_TO_SYNSET = "http://www.image-net.org/api/text/wordnet.synset.getwords?wnid={}"
  wanted = list(set([l.strip() for l in open(idfile) if l.strip() is not '' and not l.startswith("#")]))
  with open("fgo_synsets.txt", 'w') as fp:
    for wnid in wanted:
      l = ", ".join(requests.get(WNID_TO_SYNSET.format(wnid)).text.split("\n")[:-1])
      fp.write("{} {}\n".format(wnid, l))


def download_images(wnidfile, folder, n_images):
  def make_name(wnid, url):
    filename = url.replace("https://","").replace("http://","").replace("/","")
    filename = filename.split("?")[0]
    return os.path.join(folder, wnid, filename)

  URL = "http://www.image-net.org/api/text/imagenet.synset.geturls?wnid={}"
  wnids = [l.strip().split()[0] for l in open(wnidfile) if not l.startswith("#")]
  random.shuffle(wnids)
  session = requests.Session()
  for wnid in wnids:
    try:
      os.makedirs(os.path.join(folder, wnid))
    except os.error: pass
    res = requests.get(URL.format(wnid))
    urls = [_.strip() for _ in res.text.split("\n")]
    urls = [u for u in urls if u]
    jobs = [grequests.get(url, session=session, timeout=10)
        for url in urls
        if not os.path.exists(make_name(wnid, url))
    ]
    n_already_have = (len(urls) - len(jobs))
    N = max(min(n_images, len(urls)) - n_already_have, 0)
    print("getting %s, (have %d, need %d) (%d/%d)" % (wnid, n_already_have, N, wnids.index(wnid)+1, len(wnids)))
    if N == 0: continue
    curr = 0
    for res in grequests.imap(jobs, size=50):
      if curr >= N:
        print("got %d" % curr)
        break
      if res.status_code == 404 or "unavailable" in res.url:
        print(res.url, "unavailable")
        continue
      try:
        im = Image.open(BytesIO(res.content))
        if im.size[0] < 128 or im.size[1] < 128: continue
        im.save(make_name(wnid, res.url))
        print(wnid, "saved", res.url)
        curr += 1
      except IOError as e:
        print("IOError", e)
        continue
      except KeyError as e:
        print("KeyError", e)
        continue
      # except Exception as e:
      #   print("Exception", e)
      #   continue


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--wnids', default="fgo_synsets.txt")
  parser.add_argument('--folder', default="imagenet")
  parser.add_argument('-n', default=1000, type=int)
  args = parser.parse_args()
  download_images(args.wnids, args.folder, args.n)
