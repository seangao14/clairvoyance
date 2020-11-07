import numpy as np

def predict(timeline, match):
    '''
    returns [timestamps], [win%s]
    '''

    timestamps = [f['timestamp'] for f in timeline['Frames']]

    # mock for graphing
    win = np.random.normal(0,1, len(timestamps))

    return timestamps, win
