import json
import os

import numpy as np
import keras.utils as image
from tensorflow import keras

from flag_identification.settings import MODEL_PATH, W, H, LABEL_MAP_PATH, PREP_DIR


def main():

    id_map = None
    with open(LABEL_MAP_PATH, "r") as outfile:
        id_map = json.load(outfile)

    reconstructed_model = keras.models.load_model(MODEL_PATH)

    for fn in os.listdir(PREP_DIR):

        img = image.load_img(os.path.join(PREP_DIR, fn), target_size=(W, H))
        img = image.img_to_array(img)
        img = img / 255

        data = np.array([img])

        # Let's check:
        result = reconstructed_model.predict(data, verbose=0)

        predicted = id_map[
            str((result == max(result.tolist()[0])).tolist()[0].index(True))
        ]

        if fn.replace(".png", "") != predicted:
            print("==========")
            print(max(result.tolist()[0]))
            print(fn.replace(".png", ""))
            print(
                id_map[str((result == max(result.tolist()[0])).tolist()[0].index(True))]
            )


if __name__ == "__main__":
    main()
