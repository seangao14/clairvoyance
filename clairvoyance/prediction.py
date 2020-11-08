import numpy as np
from pytorch_model import Net
from game_parser import *

def load_model(path):
    model = Net()
    model.load_state_dict(torch.load(f'models/{path}', map_location=torch.device('cpu')))
    model.eval()
    return model

def predict(X, model_name='pepega1.pth'):
    '''
    an array of win%
    '''

    model = load_model(model_name)
    outputs = model(X)

    return outputs
