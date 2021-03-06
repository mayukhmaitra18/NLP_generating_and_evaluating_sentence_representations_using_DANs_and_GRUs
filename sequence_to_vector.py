# std lib imports
from typing import Dict

# external libs
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow import nn


class SequenceToVector(models.Model):
    """
    It is an abstract class defining SequenceToVector enocoder
    abstraction. To build you own SequenceToVector encoder, subclass
    this.

    Parameters
    ----------
    input_dim : ``str``
        Last dimension of the input input vector sequence that
        this SentenceToVector encoder will encounter.
    """
    def __init__(self,
                 input_dim: int) -> 'SequenceToVector':
        super(SequenceToVector, self).__init__()
        self._input_dim = input_dim

    def call(self,
             vector_sequence: tf.Tensor,
             sequence_mask: tf.Tensor,
             training=False) -> Dict[str, tf.Tensor]:
        """
        Forward pass of Main Classifier.

        Parameters
        ----------
        vector_sequence : ``tf.Tensor``
            Sequence of embedded vectors of shape (batch_size, max_tokens_num, embedding_dim)
        sequence_mask : ``tf.Tensor``
            Boolean tensor of shape (batch_size, max_tokens_num). Entries with 1 indicate that
            token is a real token, and 0 indicate that it's a padding token.
        training : ``bool``
            Whether this call is in training mode or prediction mode.
            This flag is useful while applying dropout because dropout should
            only be applied during training.

        Returns
        -------
        An output dictionary consisting of:
        combined_vector : tf.Tensor
            A tensor of shape ``(batch_size, embedding_dim)`` representing vector
            compressed from sequence of vectors.
        layer_representations : tf.Tensor
            A tensor of shape ``(batch_size, num_layers, embedding_dim)``.
            For each layer, you typically have (batch_size, embedding_dim) combined
            vectors. This is a stack of them.
        """
        # ...
        # return {"combined_vector": combined_vector,
        #         "layer_representations": layer_representations}
        raise NotImplementedError


class DanSequenceToVector(SequenceToVector):
    """
    It is a class defining Deep Averaging Network based Sequence to Vector
    encoder. You have to implement this.

    Parameters
    ----------
    input_dim : ``str``
        Last dimension of the input input vector sequence that
        this SentenceToVector encoder will encounter.
    num_layers : ``int``
        Number of layers in this DAN encoder.
    dropout : `float`
        Token dropout probability as described in the paper.
    """
    def __init__(self, input_dim: int, num_layers: int, dropout: float = 0.2):
        super(DanSequenceToVector, self).__init__(input_dim)
        # TODO(students): start
        # ...
        
        self.input_dim = input_dim
        self.num_layers = num_layers
        self.dropout = dropout
        #self.feed_frwd_net = tf.keras.layers.Dense(input_dim, activation='relu')
        
        self.feed_frwd_net = []
        for i in range(0, self.num_layers):
            self.feed_frwd_net.append(tf.keras.layers.Dense(input_dim, activation='tanh'))
        
        # TODO(students): end

    def call(self,
             vector_sequence: tf.Tensor,
             sequence_mask: tf.Tensor,
             training=False) -> tf.Tensor:
        # TODO(students): start
        # ...
        # utilising dropout
        dropout_calc = tf.math.ceil(tf.math.floor(tf.random.uniform(sequence_mask.shape,seed=1024)/self.dropout))
        sequence_mask = tf.math.multiply(sequence_mask, dropout_calc)

        # updating Sequence Mask
        seq_mask_upd = tf.math.multiply(vector_sequence, tf.multiply(tf.reshape(sequence_mask, shape=(sequence_mask.shape[0], sequence_mask.shape[1], 1)), tf.ones(shape=(1, self.input_dim))))
        mul_seq = tf.multiply(tf.reshape(tf.reduce_sum(sequence_mask, axis=1), shape=(-1, 1)), tf.ones(shape=(1, self.input_dim)))
                                    
                                    
        #calulating average                            
        average = tf.math.divide(tf.reduce_sum(seq_mask_upd, axis=1), mul_seq)
                                    
        output = []
        for i in range(0, self.num_layers):
            if i == 0:
                l = self.feed_frwd_net[i](average)
            else:
                l = self.feed_frwd_net[i](l)
            output.append(l)

        combined_vector = output[-1]
        layer_representations = tf.stack(output, axis=1)
        
        # TODO(students): end
        return {"combined_vector": combined_vector,
                "layer_representations": layer_representations}

class GruSequenceToVector(SequenceToVector):
    """
    It is a class defining GRU based Sequence To Vector encoder.
    You have to implement this.

    Parameters
    ----------
    input_dim : ``str``
        Last dimension of the input input vector sequence that
        this SentenceToVector encoder will encounter.
    num_layers : ``int``
        Number of layers in this GRU-based encoder. Note that each layer
        is a GRU encoder unlike DAN where they were feedforward based.
    """
    def __init__(self, input_dim: int, num_layers: int):
        super(GruSequenceToVector, self).__init__(input_dim)
        # TODO(students): start
        # ...
        
        self._input_dim = input_dim
        self.num_layers = num_layers

        self.gru_layer = tf.keras.layers.GRU(self._input_dim,return_sequences=True,activation='tanh')
        # TODO(students): end

    def call(self,
             vector_sequence: tf.Tensor,
             sequence_mask: tf.Tensor,
             training=False) -> tf.Tensor:
        # TODO(students): start
        # ...

        res = []
        for i in range(0, self.num_layers):
            if i == 0:
                l1 = self.gru_layer(vector_sequence,mask = sequence_mask)
            else:
                l1 = self.gru_layer(l1)
            arr = l1[:, -1, :]
            res.append(arr)
            combined_vector = arr

        layer_representations = tf.convert_to_tensor(res)
        

        # TODO(students): end
        return {"combined_vector": combined_vector,
                "layer_representations": layer_representations}