Flag Identification
===================

Given an image of a flag, identify the name of the flag.

Installation
------------

`pip install flag-identification`

Usage
-----

For any of the commands below (except `predict_flag`)

1. Run `download_flags` to get flag images
2. Run `move_additional_flags --path /path/to/repo/additional_flags` to include flags not found in wikimedia
3. Run `prepare_flags` to augment images to prepare for training
4. Run `train_flags` to get the model
5. Run `predict_flag --path {image_path}` to cycle through flags from most confident to least confident
