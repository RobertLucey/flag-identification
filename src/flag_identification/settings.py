import os

BASE_DIR = "/opt/flag_identification/"

RAW_DIR = os.path.join(BASE_DIR, "raw")
PREP_DIR = os.path.join(BASE_DIR, "prep")
AUGMENTED_DIR = os.path.join(BASE_DIR, "augmented")
MIN_LABEL_DIR = os.path.join(BASE_DIR, "min_label")
ADDITIONAL_IMAGES_DIR = os.path.join(BASE_DIR, "additional_images")
MODEL_PATH = os.path.join(BASE_DIR, "model")

LABEL_MAP_PATH = os.path.join(BASE_DIR, "label_map.json")

W = 100
H = 50
