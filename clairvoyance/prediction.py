import numpy as np
import torch
import torch.nn.functional as F

from pytorch_model import Net

def load_model(path):
    model = Net()
    model.load_state_dict(torch.load(f'models/{path}', map_location=torch.device('cpu')))
    model.eval()
    return model

def predict(game, model_name='pepega1.pth'):
    '''
    returns 1d array of win% for BLUE team from matchId
    '''
    game = torch.tensor(game).float()
    model = load_model(model_name)
    outputs = model(game)
    
    return F.softmax(outputs).detach().numpy()[:,1]

def get_gd(game):
    pass