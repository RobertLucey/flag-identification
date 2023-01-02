import shutil
import subprocess
import os
from multiprocessing import Pool

import tqdm

from flag_identification import logger


def is_text_flaggy(text):
    return any(
        [
            "flag" in text.lower(),
            "bandeira" in text.lower(),
            "bandera" in text.lower(),
            "bandiera" in text.lower(),
            "vlag" in text.lower(),
            "colours" in text.lower(),
            "govern" in text.lower(),
            "drapeau" in text.lower(),
            "ensign" in text.lower(),
            "banner" in text.lower(),
            "fiav" in text.lower(),
            "naval" in text.lower(),
            "royal" in text.lower(),
            "emblem" in text.lower(),
            "seal" in text.lower(),
            "arms" in text.lower(),
        ]
    )


def wipe_dir(path):
    try:
        shutil.rmtree(path)
    except:
        pass

    os.makedirs(path, exist_ok=True)


def clean_png(path):
    try:
        subprocess.run(["mogrify", "-format", "jpg", path])
        subprocess.run(
            [
                "mogrify",
                "-format",
                "png",
                path.replace(".png", ".jpg"),
            ],
            stdout=subprocess.DEVNULL,
        )
        os.remove(path.replace(".png", ".jpg"))
    except Exception as ex:
        logger.error(f"Could not clean file: {path}")


def clean_pngs(dir_path):
    print("Cleaning pngs")

    # check and warn if no mogrify

    pool = Pool()
    for _ in tqdm.tqdm(
        pool.imap_unordered(
            clean_png, [os.path.join(dir_path, f) for f in os.listdir(dir_path)]
        ),
        total=len(os.listdir(dir_path)),
    ):
        pass
