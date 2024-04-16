import pytest
from PIL import Image
import io


class SimulatedYOLO:
    def __init__(self, weights_path, mode):
        pass

    def __call__(self, image):
        class SimulatedResult:
            def __init__(self):
                self.names = ["cat"]

        return [SimulatedResult()]


def predict_image(image_data, model):
    image = Image.open(io.BytesIO(image_data))
    result = model(image)[0]
    return result.names[0]


@pytest.fixture
def model_fixture():
    return SimulatedYOLO('model/runs/detect/train28/weights/best.pt', 'detect')


def test_predict_image(model_fixture):
    sample_image = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = io.BytesIO()
    sample_image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()

    predicted_label = predict_image(image_data, model_fixture)
    assert predicted_label == "cat", "The prediction should be 'cat'"
