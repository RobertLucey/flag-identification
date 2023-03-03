import json
import os
import cv2

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

        result = reconstructed_model.predict(data, verbose=0)

        predicted = id_map[
            str((result == max(result.tolist()[0])).tolist()[0].index(True))
        ]

        if fn.replace(".png", "") != predicted:
            print("bad")
            score = max(result.tolist()[0])

            if score > 0.99:
                file1 = os.path.join(PREP_DIR, fn)
                file2 = os.path.join(
                    PREP_DIR,
                    id_map[
                        str((result == max(result.tolist()[0])).tolist()[0].index(True))
                    ]
                    + ".png",
                )

                img1 = cv2.imread(file1)
                img2 = cv2.imread(file2)

                img1 = cv2.resize(img1, (100, 100), interpolation=cv2.INTER_AREA)
                img2 = cv2.resize(img2, (100, 100), interpolation=cv2.INTER_AREA)

                hori = np.concatenate((img1, img2), axis=1)

                cv2.imshow("HORIZONTAL", hori)

                k = cv2.waitKey(0)  # current catched key

                if k == ord("y"):
                    print("same")
                elif k == ord("n"):
                    print("diff")

                cv2.destroyAllWindows()

                # print("==========")
                # print(score)
                # print(fn.replace(".png", ""))
                # print(
                #    id_map[str((result == max(result.tolist()[0])).tolist()[0].index(True))]
                # )

                # If they're the same keep the one with the longer name
                # put into a config somewhere so on prep we can avoid putting into the prep dir

                # should be a manual thing
        else:
            print("good")


if __name__ == "__main__":
    main()
