Flag Identification
===================

Given an image of a flag, identify the name of the flag.

Installation
------------

`pip install flag-identification`

Usage
-----

For any of the commands below (except `predict_flag`), from the repo you can run `make {command}`.

1. Run `download_flags` to get flag images
2. Run `prepare_flags` to augment images to prepare for training
3. Run `train_flags` to get the model
4. Run `predict_flag --path {image_path}` to get the predicted image
