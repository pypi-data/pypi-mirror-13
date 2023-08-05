from .. import backend as T
import numpy as np

from ..node import RecurrentNode, Data

class LSTM(RecurrentNode):

    def __init__(self, shape_in, shape_out=None,
                 use_forget_gate=True,
                 use_input_peep=False,
                 use_output_peep=False,
                 use_forget_peep=False,
                 use_tanh_output=True):

        super(LSTM, self).__init__()
        if shape_out is None:
            self.shape_in = None
            self.shape_out = shape_in
        else:
            self.shape_in = shape_in
            self.shape_out = shape_out

        self.use_forget_gate = use_forget_gate
        self.use_input_peep = use_input_peep
        self.use_output_peep = use_output_peep
        self.use_forget_peep = use_forget_peep
        self.use_tanh_output = use_tanh_output

    def copy(self):
        return LSTM(self.get_shape_in(),
                    self.get_shape_out(),
                    use_forget_gate=self.use_forget_gate,
                    use_input_peep=self.use_input_peep,
                    use_output_peep=self.use_output_peep,
                    use_forget_peep=self.use_forget_peep,
                    use_tanh_output=self.use_tanh_output,
                    )

    def _infer(self, shape_in):
        return self.shape_out

    def create_lstm_parameters(self, shape_in, shape_out, layer):
        params = {}
        params['Wi'] = self.init_parameter('W_ix-%u' % layer, (shape_in, shape_out))
        params['Ui'] = self.init_parameter('U_ih-%u' % layer, (shape_out, shape_out))
        params['bi'] = self.init_parameter('b_i-%u' % layer, shape_out)

        params['Wo'] = self.init_parameter('W_ox-%u' % layer, (shape_in, shape_out))
        params['Uo'] = self.init_parameter('U_oh-%u' % layer, (shape_out, shape_out))
        params['bo'] = self.init_parameter('b_o-%u' % layer, shape_out)

        if self.use_forget_gate:
            params['Wf'] = self.init_parameter('W_fx-%u' % layer, (shape_in, shape_out))
            params['Uf'] = self.init_parameter('U_fx-%u' % layer, (shape_out, shape_out))
            params['bf'] = self.init_parameter('b_f-%u' % layer, shape_out)

        params['Wg'] = self.init_parameter('W_gx-%u' % layer, (shape_in, shape_out))
        params['Ug'] = self.init_parameter('U_gx-%u' % layer, (shape_out, shape_out))
        params['bg'] = self.init_parameter('b_g-%u' % layer, shape_out)

        if self.use_input_peep:
            params['Pi'] = self.init_parameter('P_i-%u' % layer, (shape_out, shape_out))
        if self.use_output_peep:
            params['Po'] = self.init_parameter('P_o-%u' % layer, (shape_out, shape_out))
        if self.use_forget_peep:
            params['Pf'] = self.init_parameter('P_f-%u' % layer, (shape_out, shape_out))
        return params

    def initialize(self):
        shape_in, shape_out = self.get_shape_in(), self.get_shape_out()
        self.params = self.create_lstm_parameters(shape_in, shape_out, 0)

    def _forward(self, X):
        S, N, D = T.shape(X)

        H = self.get_shape_out()

        def step(input, previous):
            previous_hidden, previous_state = previous
            lstm_hidden, state = self.step(input, previous_hidden, previous_state, self.params)
            return lstm_hidden, [lstm_hidden, state]

        hidden = T.alloc(0, (N, H))
        state = T.alloc(0, (N, H))

        last_output, output, new_state = T.rnn(step,
                              X,
                              [hidden, state])
        return output

    def step(self, X, previous_hidden, previous_state, params):
        Wi, Ui, bi = params['Wi'], params['Ui'], params['bi']
        if self.use_input_peep:
            Pi = params['Pi']
            input_gate = T.sigmoid(T.dot(X, Wi) + T.dot(previous_hidden, Ui) + T.dot(previous_state, Pi) + bi)
        else:
            input_gate = T.sigmoid(T.dot(X, Wi) + T.dot(previous_hidden, Ui) + bi)

        Wg, Ug, bg = params['Wg'], params['Ug'], params['bg']
        candidate_state = T.tanh(T.dot(X, Wg) + T.dot(previous_hidden, Ug) + bg)

        if self.use_forget_gate:
            Wf, Uf, bf = params['Wf'], params['Uf'], params['bf']
            if self.use_forget_peep:
                Pf = params['Pf']
                forget_gate = T.sigmoid(T.dot(X, Wf) + T.dot(previous_hidden, Uf) + T.dot(previous_state, Pf) + bf)
            else:
                forget_gate = T.sigmoid(T.dot(X, Wf) + T.dot(previous_hidden, Uf) + bf)
            state = candidate_state * input_gate + previous_state * forget_gate
        else:
            state = candidate_state * input_gate + previous_state * 0

        Wo, Uo, bo = params['Wo'], params['Uo'], params['bo']
        if self.use_output_peep:
            Po = params['Po']
            output_gate = T.sigmoid(T.dot(X, Wo) + T.dot(previous_hidden, Uo) + T.dot(previous_state, Po) + bo)
        else:
            output_gate = T.sigmoid(T.dot(X, Wo) + T.dot(previous_hidden, Uo) + bo)
        if self.use_tanh_output:
            output = output_gate * T.tanh(state)
        else:
            output = output_gate * state
        return output, state

    def get_previous_zeros(self, N):
        return T.alloc(0, (N, self.get_shape_out())), T.alloc(0, (N, self.get_shape_out()))

class MultilayerLSTM(LSTM):

    def __init__(self, shape_in, shape_out=None,
                 **kwargs):
        num_layers = kwargs.pop('num_layers', 2)
        super(MultilayerLSTM, self).__init__(shape_in,
                                   shape_out=shape_out,
                                   **kwargs)
        self.num_layers = num_layers
        assert self.num_layers >= 1, "Invalid number of layers"

    def initialize(self):
        shape_in, shape_out = self.get_shape_in(), self.get_shape_out()
        self.params = []
        self.params.append(self.create_lstm_parameters(shape_in, shape_out, 0))
        for i in xrange(1, self.num_layers):
            self.params.append(self.create_lstm_parameters(shape_out, shape_out, i))

    def _forward(self, X):
        S, N, D = T.shape(X)

        H = self.get_shape_out()

        def step(input, previous):
            previous_hidden, previous_state = previous
            hiddens, states = [], []
            lstm_hidden = input
            for i in xrange(self.num_layers):
                lstm_hidden, state = self.step(lstm_hidden, previous_hidden[i, :, :], previous_state[i, :, :], self.params[i])
                hiddens.append(lstm_hidden)
                states.append(state)
            return lstm_hidden, [T.stack(hiddens), T.stack(states)]

        hidden = T.alloc(0, (self.num_layers, N, H))
        state = T.alloc(0, (self.num_layers, N, H))

        last_output, output, new_state = T.rnn(step,
                              X,
                              [hidden, state])
        return output
