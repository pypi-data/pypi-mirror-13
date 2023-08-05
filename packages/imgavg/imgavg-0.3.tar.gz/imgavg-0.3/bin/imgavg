#!/usr/bin/env python3

from imgavg import imgavg


def main():
    args = imgavg.parse()

    try:
        imgavg.average(args)
    except (imgavg.InconsistentImageError, imgavg.InsufficientImagesError) as e:
        print(e)


if __name__ == "__main__":
    main()
