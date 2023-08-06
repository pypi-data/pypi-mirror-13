# -*- coding: utf-8 -*-

r'''Tree layers for neural network computation graphs.

Tree layers are those that are explicitly designed to incorporate multiple
inputs.
'''

from __future__ import division

import climate
import numpy as np
import theano
import theano.tensor as TT

from . import base
from .. import util

logging = climate.get_logger(__name__)

FLOAT = theano.config.floatX

__all__ = [
    'Tree',
    'NaryLSTM',
]


class Tree(base.Layer):
    r'''A tree network layer incorporates multiple inputs.

    In many respects, a tree layer is much like a basic feedforward layer: both
    layers take an input signal, apply some transformation to it, and produce an
    output signal. Tree layers, however, are explicitly designed to incorporate
    inputs from multiple other layers.

    This layer type is actually just a base class for the different (current and
    future) types of tree layers.
    '''


class NaryLSTM(Tree):
    r'''An LSTM-inspired layer with N inputs.

    An LSTM layer is composed of a number of "cells" that are explicitly
    designed to store information for a certain period of time. Each cell's
    stored value is "guarded" by three gates that permit or deny modification of
    the cell's value:

    - The "input" gate turns on when the input to the LSTM layer should
      influence the cell's value.
    - The "output" gate turns on when the cell's stored value should propagate
      to the next layer.
    - The "forget" gate turns on when the cell's stored value should be reset.

    The output :math:`h_t` of the LSTM layer at time :math:`t` is given as a
    function of the input :math:`x_t` and the previous states of the layer
    :math:`h_{t-1}` and the internal cell :math:`c_{t-1}` by:

    .. math::
       \begin{eqnarray}
       i_t &=& \sigma(x_t W_{xi} + h_{t-1} W_{hi} + c_{t-1} W_{ci} + b_i) \\
       f_t &=& \sigma(x_t W_{xf} + h_{t-1} W_{hf} + c_{t-1} W_{cf} + b_f) \\
       c_t &=& f_t c_{t-1} + i_t \tanh(x_t W_{xc} + h_{t-1} W_{hc} + b_c) \\
       o_t &=& \sigma(x_t W_{xo} + h_{t-1} W_{ho} + c_t W_{co} + b_o) \\
       h_t &=& o_t \tanh(c_t)
       \end{eqnarray}

    where the :math:`W_{ab}` are weight matrix parameters and the :math:`b_x`
    are bias vectors. Equations (1), (2), and (4) give the activations for the
    three gates in the LSTM unit; these gates are activated using the logistic
    sigmoid so that their activities are confined to the open interval (0, 1).
    The value of the cell is updated by equation (3) and is just the weighted
    sum of the previous cell value and the new cell value, where the weights are
    given by the forget and input gate activations, respectively. The output of
    the unit is the cell value weighted by the activation of the output gate.

    References
    ----------

    .. [Tai15] K. S. Tai, R. Socher, & C. D. Manning. (2015) "Improved Semantic
       Representations From Tree-Structured Long Short-Term Memory Networks."
       http://arxiv.org/abs/1503.00075
    '''

    def setup(self):
        '''Set up the parameters and initial values for this layer.'''
        self.add_weights('xh', self.input_size, 4 * self.size)
        self.add_weights('hh', self.size, 4 * self.size)
        self.add_bias('b', 4 * self.size, mean=2)
        # the three "peephole" weight matrices are always diagonal.
        self.add_bias('ci', self.size)
        self.add_bias('cf', self.size)
        self.add_bias('co', self.size)

    def transform(self, inputs):
        '''Transform the inputs for this layer into an output for the layer.

        Parameters
        ----------
        inputs : dict of theano expressions
            Symbolic inputs to this layer, given as a dictionary mapping string
            names to Theano expressions. See :func:`base.Layer.connect`.

        Returns
        -------
        outputs : dict of theano expressions
            A map from string output names to Theano expressions for the outputs
            from this layer. This layer type generates a "cell" output that
            gives the value of each hidden cell in the layer, and an "out"
            output that gives the actual gated output from the layer.
        updates : list of update pairs
            A sequence of updates to apply inside a theano function.
        '''
        def split(z):
            n = self.size
            return z[:, 0*n:1*n], z[:, 1*n:2*n], z[:, 2*n:3*n], z[:, 3*n:4*n]

        def fn(x_t, h_tm1, c_tm1):
            xi, xf, xc, xo = split(x_t + TT.dot(h_tm1, self.find('hh')))
            i_t = TT.nnet.sigmoid(xi + c_tm1 * self.find('ci'))
            f_t = TT.nnet.sigmoid(xf + c_tm1 * self.find('cf'))
            c_t = f_t * c_tm1 + i_t * TT.tanh(xc)
            o_t = TT.nnet.sigmoid(xo + c_t * self.find('co'))
            h_t = o_t * TT.tanh(c_t)
            return [h_t, c_t]

        # input is:   (batch, time, input)
        # scan wants: (time, batch, input)
        x = self._only_input(inputs).dimshuffle(1, 0, 2)

        batch_size = x.shape[1]
        (o, c), updates = self._scan(
            fn,
            [TT.dot(x, self.find('xh')) + self.find('b')],
            [('h', batch_size), ('c', batch_size)])

        # output is:  (time, batch, output)
        # we want:    (batch, time, output)
        out = o.dimshuffle(1, 0, 2)
        cell = c.dimshuffle(1, 0, 2)

        return dict(out=out, cell=cell), updates
