import cv2
import unicodedata
import os
import shutil
import tqdm
import random
from multiprocessing import Pool
from distutils.dir_util import copy_tree

import imgaug.augmenters as iaa
from flag_identification.settings import RAW_DIR, AUGMENTED_DIR, ADDITIONAL_IMAGES_DIR, PREP_DIR, W, H
from flag_identification.utils import wipe_dir, clean_pngs


def mod_file(args):

    count, f = args

    if not f.endswith(".png") or f.startswith("tmp"):
        return

    image = cv2.imread(os.path.join(PREP_DIR, f), 1)

    # resize for speed
    image = cv2.resize(image, (W, H), interpolation=cv2.INTER_AREA)

    for i in range(count):

        img = image
        border_colour = [
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(0, 50),
        ]
        if random.random() < 0.4:
            top, bottom = [random.randint(0, int(H / 4))] * 2
            left, right = [random.randint(0, int(H / 4))] * 2
            color = [255, 255, 255]
            img = cv2.copyMakeBorder(
                img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
            )

        if random.random() < 0.8:
            center = (W // 2, H // 2)
            M = cv2.getRotationMatrix2D(center, random.randint(-25, 25), 1.0)
            img = cv2.warpAffine(
                image,
                M,
                (W, H),
                borderValue=border_colour,
                borderMode=cv2.BORDER_CONSTANT,
            )

        if random.random() < 0.2:
            top, bottom = [random.randint(0, int(H / 4))] * 2
            left, right = [random.randint(0, int(H / 4))] * 2
            img = cv2.copyMakeBorder(
                img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=border_colour
            )

        augmentations = [
            iaa.MotionBlur(k=3, angle=[-45, 45]),
            iaa.ElasticTransformation(alpha=(0, 5.0), sigma=0.25),
            iaa.PerspectiveTransform(scale=(0.001, 0.05)),
            iaa.PiecewiseAffine(scale=(0.001, 0.05)),
            iaa.Sharpen(alpha=(0.0, 1.0), lightness=(0.75, 2.0)),
            iaa.Affine(scale=(0.5, 1.5)),
        ]

        seq = iaa.Sequential(
            random.sample(augmentations, random.randint(0, len(augmentations)))
        )

        images_aug = seq(images=[img])

        name = f.replace(".png", "")

        # put to other target dir
        cv2.imwrite(
            os.path.join(AUGMENTED_DIR, name + "_" + str(i) + ".png"),
            images_aug[0],
        )


def populate_prep():

    # TODO: warn of dups

    wipe_dir(PREP_DIR)

    copy_tree(ADDITIONAL_IMAGES_DIR, PREP_DIR)

    print(f"Moving pngs from {RAW_DIR} to {PREP_DIR}")
    labels = set()
    for f in os.listdir(RAW_DIR):
        label = f.split("_")[-1].replace("–", "-")
        label = unicodedata.normalize("NFKD", label).encode("ASCII", "ignore")
        label = str(label, "utf-8")
        label = label.replace(' of ', ' ')
        label = label.replace(' ', '-')
        label = label.lower()

        if label not in labels:
            shutil.copyfile(os.path.join(RAW_DIR, f), os.path.join(PREP_DIR, label))
            labels.add(label)


def main():
    populate_prep()

    # Only do this if mogrify installed
    clean_pngs(PREP_DIR)

    wipe_dir(AUGMENTED_DIR)

    pool = Pool()
    for _ in tqdm.tqdm(
        pool.imap_unordered(mod_file, [(100, f) for f in os.listdir(PREP_DIR)]),
        total=len(os.listdir(PREP_DIR)),
    ):
        pass


if __name__ == "__main__":
    main()
