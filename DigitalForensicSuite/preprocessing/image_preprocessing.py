"""Resize, normalize, and generate Error Level Analysis (ELA) images for the
image forgery detection CNN.

Pipeline: original -> resave as JPEG (Q=95) -> pixelwise diff -> enhance -> ELA image
"""


def generate_ela_image(image_path: str, quality: int = 95):
    raise NotImplementedError


def preprocess_image(image_path: str, size: tuple = (256, 256)):
    raise NotImplementedError
