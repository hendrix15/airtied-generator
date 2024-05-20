from generation.model import TowerModel
import torch
from util.obj_reader import write_result_to_file

def predict():
    model = TowerModel()
    model.load_state_dict(torch.load("demo_model.pt"))
    model.eval()

    result = model(torch.tensor([[200]], dtype=torch.float32))
    write_result_to_file(result, "result.obj")


if __name__ == "__main__":
    predict()