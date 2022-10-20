import random
import sys

import numpy as np
import tensorflow as tf

from Player import AIPlayer

class DeepQPlayer(AIPlayer):

    def __init__(self, model, rewards, buffers, buffer_size, epsilon, delay=0, name=None):
        super().__init__(delay, name)
        self.model = model
        self.buffers = buffers
        self.epsilon = epsilon
        self.rewards = rewards
        self.buffer_size = buffer_size

    def _make_move(self, board, retry):
        move = self.get_move(board, retry)
        state = [*board, self.mark]

        self.buffers['action_history'].append(move)
        self.buffers['state_history'].append(state)
        if len(self.buffers['state_history']) > 1:
            self.buffers['state_next_history'].append(state)
        self.buffers['rewards_history'].append(self.rewards['move'])
        self.buffers['done_history'].append(False)

        if len(self.buffers['action_history']) > self.buffer_size:
            for buffer in self.buffers.values():
                del buffer[:1]

        return move

    def get_move(self, board, retry):
        if self.epsilon > np.random.rand(1)[0]:
            return self.get_random_move(board, retry)
        else:
            return self.get_greedy_move(board, retry)

    def get_random_move(self, board, retry):
        valid_moves = np.where(np.array(board) == 0)[0]
        return random.choice(valid_moves)

    def get_greedy_move(self, board, retry):
        state = [*board, self.mark]
        # Predict action Q-values
        # From environment state
        state_tensor = tf.convert_to_tensor(state)
        state_tensor = tf.expand_dims(state_tensor, 0)
        action_probs = self.model(state_tensor, training=False)
        # Take best action
        invalid_moves = tf.convert_to_tensor([np.inf if x != 0 else float(0) for x in board])
        action_probs += invalid_moves
        action = tf.argmax(action_probs[0]).numpy()
        return action

    def get_episode_data(self):
        pass

    def win(self):
        super().win()
        self.buffers['state_next_history'].append([-1] * 10)
        self.buffers['rewards_history'][-1] = self.rewards['win']
        self.buffers['done_history'][-1] = True
        

    def lose(self):
        super().lose()
        self.buffers['state_next_history'].append([-1] * 10)
        self.buffers['rewards_history'][-1] = self.rewards['lose']
        self.buffers['done_history'][-1] = True

    def tie(self):
        super().tie()
        self.buffers['state_next_history'].append([-1] * 10)
        self.buffers['rewards_history'][-1] = self.rewards['tie']
        self.buffers['done_history'][-1] = True