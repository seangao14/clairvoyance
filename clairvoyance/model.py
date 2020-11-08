import torch
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.champ_fc1 = nn.Linear(304, 50, bias=False)
        self.champ_fc2 = nn.Linear(50, 20, bias=False)
        self.fc1 = nn.Linear(45, 32, bias=False)
        self.d1 = nn.Dropout(0.2)
        self.fc2 = nn.Linear(32, 2)

    
    def forward(self, x):
        c = self.champ_fc1(x[:, 1:305])
        c = F.leaky_relu(c)
        c = self.champ_fc2(c)
        c = F.leaky_relu(c)
        a = 1/500000
        c = torch.mul(torch.tensor(a), c)

        # n for new
        n = torch.cat((x[:, 0:1], c), dim=1)
        n = torch.cat((n, x[:, 305:]), dim=1)

        # print(n.shape)
        x = self.fc1(n)
        x = F.leaky_relu(x)
        x = self.d1(x)

        x = self.fc2(x)
        return x