import numpy as np

def load_model(path):
    model = nn.Sequential(*features)
    model.load_state_dict(torch.load(f'models/{path}', map_location=torch.device('cpu')))
    model.eval()
    return model

def predict(timeline, match):
    '''
    returns [timestamps], [win%s]
    '''

    timestamps = [f['timestamp'] for f in timeline['Frames']]

    # mock for graphing
    win = np.random.normal(0,1, len(timestamps))

    return timestamps, win
