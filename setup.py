from setuptools import find_packages, setup

INSTALL_REQUIRES = (
    "imgaug",
    "aspose-words",
    "cairosvg",
    "bs4",
    "keras==2.11.0",
    "tensorflow==2.11.0",
    "cython",
    "tqdm",
    "requests",
    "pandas",
    "sklearn",
    "scikit-learn",
    "Pillow",
    "opencv-python",
)

setup(
    name="flag_identification",
    version="0.0.7",
    python_requires=">=3.6",
    description="Identify a flag by an image",
    long_description="Identify a flag by an image",
    author="Robert Lucey",
    url="https://github.com/RobertLucey/flag-identification",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "download_flags = flag_identification.bin.pull_wikimedia:main",
            "prepare_flags = flag_identification.bin.prep:main",
            "train_flags = flag_identification.bin.train:main",
            "predict_flag = flag_identification.bin.predict_single:main",
            "move_additional_flags = flag_identification.bin.move_additional_flags:main",
        ]
    },
)
