#!/usr/bin/env python3

import argparse
import os

import numpy as np
from PIL import Image


class InconsistentImageError(Exception):
    """thrown when a selection of images are not the same dimensions"""
    pass


class InsufficientImagesError(Exception):
    """thrown when there are not enough images to average"""
    pass

def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--folder", default=".", help="The folder to load images from")
    parser.add_argument("-o", "--output", default="out.png", help="filename of the resulting image")
    parser.add_argument("-v", "--verbose", action="store_true", help="print more verbose output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Silence all printed output")

    args = parser.parse_args()

    return vars(args)


def flush(args):
    if not args["verbose"] and not args["quiet"]:
        print("", flush=False)


def average(args):

    data = None
    files = [os.path.join(args["folder"], item) for item in os.listdir(args["folder"]) if any(ext in item for ext in ["png", "jpg", "bmp"])]

    # break out if there are no images, to avoid division by zero below
    if not len(files):
        raise InsufficientImagesError("no images found in {}".format(os.path.abspath(args["folder"])))

    # The whole process is useless if there isnt at least two images, break out.
    if len(files) <= 1:
        raise InsufficientImagesError("not enough images to average")

    try:
        for path in files:
            im = Image.open(path)
            temp_arr = np.array(im).astype(np.uint64)

            if data is None: #populate the array
                data = temp_arr
            elif data.shape != temp_arr.shape: #throw if image dimensions differ
                flush(args)
                raise InconsistentImageError("images must all be the same dimensions, and have the same bands E.G.(RGB, RGBA)")
            else:
                data += temp_arr

            if not args["quiet"]:
                if args["verbose"]:
                    print("loaded {}".format(path))
                else:
                    print('.', end="", flush=True)
    except TypeError:
        # If the user attempts to cancel the process, we'll jump out of the loop
        # and save the result
        pass


    flush(args)

    result = data / len(files)

    im = Image.fromarray(result.astype(np.uint8))

    if args["verbose"]:
        print("saving {}".format(args["output"]))

    im.save(args["output"])
    return result
