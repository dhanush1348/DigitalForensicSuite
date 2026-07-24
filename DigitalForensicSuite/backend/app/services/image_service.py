"""Service layer: loads model, runs preprocessing + inference, formats response.
Kept separate from routers so training/inference code can be unit-tested
without spinning up FastAPI.
"""


async def predict(file):
    # TODO: implement (see inference/predict_image.py once model is trained)
    raise NotImplementedError
