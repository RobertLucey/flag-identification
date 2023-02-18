import argparse
import os
from distutils.dir_util import copy_tree

from flag_identification.settings import ADDITIONAL_IMAGES_DIR


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", dest="path", help="path", required=True)
    args = parser.parse_args()

    os.makedirs(ADDITIONAL_IMAGES_DIR, exist_ok=True)

    copy_tree(args.path, ADDITIONAL_IMAGES_DIR)


if __name__ == "__main__":
    main()
