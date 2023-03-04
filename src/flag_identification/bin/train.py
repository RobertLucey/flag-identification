import json
import random
import os
from collections import defaultdict
from multiprocessing import Pool

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
import keras.utils as image
import numpy as np
from tqdm import tqdm

from flag_identification import logger
from flag_identification.settings import (
    AUGMENTED_DIR,
    MODEL_PATH,
    W,
    H,
    LABEL_MAP_PATH,
    PREP_DIR,
)


def get_dataframe(flags_to_use):
    flags_set = set([f.replace(".png", "") for f in flags_to_use])

    images_to_use = [
        f
        for f in os.listdir(AUGMENTED_DIR)
        if f.replace(".png", "").split("_")[0] in flags_set
    ]

    image_files = sorted(images_to_use)

    flags_set = []
    for idx, f in enumerate(image_files):
        if not f.endswith(".png"):
            continue

        label = f.split("_")[0]
        flags_set.append(label)

    flags_set = sorted(list(set(flags_set)))

    dd = defaultdict(list)
    for idx, f in tqdm(enumerate(image_files), total=len(image_files)):
        if not f.endswith(".png"):
            continue

        label = f.split("_")[0]

        for i in flags_set:
            dd[i].append(label == i)

    return dict(dd)


def get_model(classes):
    model = Sequential()

    model.add(
        Conv2D(filters=32, kernel_size=(5, 5), activation="relu", input_shape=(W, H, 3))
    )
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.5))
    model.add(Conv2D(64, (5, 5), padding="same", activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(512, activation="relu"))
    model.add(Dropout(0.6))
    model.add(Dense(len(classes), activation="sigmoid"))

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy", "top_k_categorical_accuracy"],
    )

    return model


def split_train_test(images, df):
    df_keys = df.keys()

    x_train = []
    y_train = []
    x_test = []
    y_test = []

    # Not using standard tools here due to them using too much memory
    # Build up the label indexes now

    logger.info("split training")

    pbar = tqdm(total=len(images))
    idx = len(images) - 1
    while images:
        img = images.pop()
        if random.random() < 0.9:
            x_train.append(img)
            y_train_sub = []
            for key in df_keys:
                y_train_sub.append(df[key][idx])
            y_train.append(np.array(y_train_sub))

        else:
            x_test.append(img)
            y_test_sub = []
            for key in df_keys:
                y_test_sub.append(df[key][idx])
            y_test.append(np.array(y_test_sub))

        idx -= 1

        pbar.update(1)

    pbar.close()

    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)

    logger.info("finished split training")

    return x_train, y_train, x_test, y_test


def _get_image(f):
    img = image.load_img(os.path.join(AUGMENTED_DIR, f), target_size=(W, H, 3))
    img = image.img_to_array(img)
    img = img / 255
    return img


def get_images(df):
    images = []
    pool = Pool()
    all_files = os.listdir(AUGMENTED_DIR)
    for label in tqdm(df.keys()):
        files = [f for f in all_files if f.startswith(label + "_")]
        for img in pool.imap_unordered(_get_image, files):
            images.append(img)

    return images


def chunks(l, n):
    """
    Yields chunks of a list

    :param l: list to chunk
    :param n: number of items to chunk by
    :return:
    :rtype: list
    """
    for i in range(0, len(l), n):
        yield l[i : i + n]


def main():

    prep_files = os.listdir(PREP_DIR)

    range_max = int(len(prep_files) / 300)

    for idx in range(range_max):
        print(f"STARTING ROUND {idx + 1}")

        # split into range_max and select idx of os.path.listdir(PREP_DIR)
        flags_to_use = list(chunks(prep_files, int(len(prep_files) / range_max)))[idx]

        logger.info("get dataframe")
        df = get_dataframe(flags_to_use)
        logger.info("finished getting dataframe")

        logger.info("saving label map")
        id_map = {i: l for i, l in enumerate(df.keys())}
        with open(f"{LABEL_MAP_PATH}_{idx}", "w") as outfile:
            json.dump(id_map, outfile)
        logger.info("finished saving label map")

        logger.info("load images")
        images = get_images(df)
        logger.info("finished loading images")

        df_items_len = len(df[list(df.keys())[0]])
        if df_items_len != len(images):
            logger.info(
                f"Records in df {df_items_len} does not equal the number of images {len(images)}"
            )

        logger.info("splitting train / test")
        x_train, y_train, x_test, y_test = split_train_test(images, df)
        images = []
        logger.info("finished splitting train / test")

        classes = list(df.keys())
        model = get_model(classes)

        model.fit(
            x_train,
            y_train,
            epochs=4,
            validation_data=(x_test, y_test),
            batch_size=64,
        )

        model.save(f"{MODEL_PATH}_{idx}")


if __name__ == "__main__":
    main()
