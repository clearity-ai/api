"""Utils for model saving and loading"""
from pathlib import Path
import pickle


def save_model(model, model_path):
    """Save model as pickle"""
    model = model.cpu()
    model_dict = {"state_dict": model.state_dict(), "hparams": model.hparams}
    model_path = Path(model_path)
    pickle.dump(model_dict, open(model_path, "wb", 4))
    return model_path


def load_model(model_class, model_path):
    """Load model from pickle"""
    model_path = Path(model_path)
    model_dict = pickle.load(open(model_path, "rb", 4))
    model = model_class(hparams=model_dict["hparams"])
    model.load_state_dict(model_dict["state_dict"])
    model.eval()
    return model
