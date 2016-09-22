import argparse
import json
import numpy as np
import scipy.signal


def convert(X, labels, k=5, decim=1):
    top_k = X.sum(0).argsort()[-k:][::-1]
    X = X[:X.shape[0] / 5., top_k]
    freq = X.sum(0)
    # X_grouped = X.reshape((-1, ntiles, X.shape[1])).sum(1).reshape((-1, X.shape[1]))
    X_grouped = X
    top = scipy.signal.decimate(X_grouped, q=decim, axis=0)
    top = X_grouped
    top[top < 0] = 0
    top = top / top.max()
    terms = [labels[str(x)] for x in top_k]
    return {'data': top.T.tolist(), 'labels': terms, 'freq': freq.tolist(), 'x': list(range(top.shape[0])), 'downsampled': decim}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("npy")
    parser.add_argument("labels")
    parser.add_argument("-o", dest='json')
    parser.add_argument("--topk", default=5, type=int)
    args = parser.parse_args()

    with open(args.labels) as labels_fp:
        data = convert(np.load(args.npy), json.load(labels_fp), args.topk)
        data.update({'name': ".".join(args.json.split("/")[-1].split(".")[:-1])})
        with open(args.json, 'w') as json_fp:
            json.dump(data, json_fp)
