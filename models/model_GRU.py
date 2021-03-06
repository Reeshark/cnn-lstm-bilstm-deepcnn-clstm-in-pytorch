import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np
import random
import hyperparams
torch.manual_seed(hyperparams.seed_num)
random.seed(hyperparams.seed_num)

"""
Neural Networks model : GRU
"""


class GRU(nn.Module):
    
    def __init__(self, args):
        super(GRU, self).__init__()
        self.args = args
        self.hidden_dim = args.lstm_hidden_dim
        self.num_layers = args.lstm_num_layers
        V = args.embed_num
        D = args.embed_dim
        C = args.class_num
        self.embed = nn.Embedding(V, D)
        # word embedding
        if args.word_Embedding:
            pretrained_weight = np.array(args.pretrained_weight)
            self.embed.weight.data.copy_(torch.from_numpy(pretrained_weight))
        # gru
        self.gru = nn.GRU(D, self.hidden_dim, dropout=args.dropout, num_layers=self.num_layers)
        # linear
        self.hidden2label = nn.Linear(self.hidden_dim, C)
        # hidden
        self.hidden = self.init_hidden(self.num_layers, args.batch_size)
        # dropout
        self.dropout = nn.Dropout(args.dropout)

    def init_hidden(self, num_layers, batch_size):
        if self.args.cuda is True:
            return Variable(torch.zeros(num_layers, batch_size, self.hidden_dim)).cuda()
        else:
            return Variable(torch.zeros(num_layers, batch_size, self.hidden_dim))

    def forward(self, input):
        self.hidden = self.init_hidden(self.num_layers, input.size(1))
        embed = self.embed(input)
        input = embed.view(len(input), embed.size(1), -1)
        lstm_out, hidden = self.gru(input, self.hidden)
        lstm_out = torch.transpose(lstm_out, 0, 1)
        lstm_out = torch.transpose(lstm_out, 1, 2)
        # pooling
        lstm_out = F.max_pool1d(lstm_out, lstm_out.size(2)).squeeze(2)
        lstm_out = F.tanh(lstm_out)
        # linear
        y = self.hidden2label(lstm_out)
        logit = y
        return logit