import json
import argparse
import os

import cv2

import numpy as np
import keras.utils as image
from tensorflow import keras

from flag_identification.settings import (
    MODEL_PATH,
    W,
    H,
    LABEL_MAP_PATH,
    PREP_DIR,
    BASE_DIR,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--path", dest="path", help="path")

    args = parser.parse_args()

    model_paths = []
    for f in os.listdir(BASE_DIR):
        if f.startswith("model_"):
            model_paths.append(os.path.join(BASE_DIR, f))

    id_map = {}
    models = []
    for idx, model in enumerate(model_paths):
        with open(f"{LABEL_MAP_PATH}_{idx}", "r") as outfile:
            id_map[idx] = json.load(outfile)

        models.append(keras.models.load_model(f"{MODEL_PATH}_{idx}"))

    img = image.load_img(args.path, target_size=(W, H))
    img = image.img_to_array(img)
    img = img / 255

    data = np.array([img])

    results = []
    for idx, model in enumerate(models):
        predictions = model.predict(data, verbose=0)[0].tolist()
        for pidx, p in enumerate(predictions):
            results.append((id_map[idx][str(pidx)], p))

    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    sum_scores = sum([i[1] for i in sorted_results])

    for value in sorted_results:

        score = value[1] / sum_scores

        print(f"{score}: {value[0]}")

        img = cv2.imread(os.path.join(PREP_DIR, value[0] + ".png"))

        cv2.imshow(f"{value[0]}: {score}   (any key to continue, q to exit)", img)

        k = cv2.waitKey(0)  # current catched key

        cv2.destroyAllWindows()

        if k == ord("q"):
            break


if __name__ == "__main__":
    main()
