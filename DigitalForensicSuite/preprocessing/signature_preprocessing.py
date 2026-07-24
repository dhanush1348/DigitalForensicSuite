"""Grayscale -> Otsu threshold -> binarize -> morphological cleaning -> resize
-> normalize, for the signature verification Siamese network.
"""


def preprocess_signature(image_path: str, size: tuple = (256, 256)):
    raise NotImplementedError
