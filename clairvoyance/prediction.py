import numpy as np
import torch
import torch.nn.functional as F

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
    X = torch.tensor(X).float()
    model = load_model(model_name)
    outputs = model(X)
    
    return F.softmax(outputs).detach().numpy()
