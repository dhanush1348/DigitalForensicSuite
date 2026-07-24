"""Service layer: loads model, runs preprocessing + inference, formats response.
Kept separate from routers so training/inference code can be unit-tested
without spinning up FastAPI.
"""


async def compare(reference, questioned):
    # TODO: implement (see inference/predict_signature.py once model is trained)
    raise NotImplementedError
