from baselines.common.atari_wrappers import make_atari, wrap_deepmind
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
from DeepQPlayer import DeepQPlayer
from Player import HumanPlayer
from tqdm import tqdm


from tictactoe import TicTacToe

# Configuration paramaters for the whole setup
seed = 42
gamma = 0.99  # Discount factor for past rewards
epsilon = 1.0  # Epsilon greedy parameter
epsilon_min = 0.1  # Minimum epsilon greedy parameter
epsilon_max = 1.0  # Maximum epsilon greedy parameter
epsilon_interval = (
    epsilon_max - epsilon_min
)  # Rate at which to reduce chance of random action being taken
batch_size = 32  # Size of batch taken from replay buffer

# # Use the Baseline Atari environment because of Deepmind helper functions
# env = make_atari("BreakoutNoFrameskip-v4")
# # Warp the frames, grey scale, stake four frame and scale to smaller ratio
# env = wrap_deepmind(env, frame_stack=True, scale=True)
# env.seed(seed)

num_actions = 9


def create_q_model():
    # Network defined by the Deepmind paper
    inputs = layers.Input(shape=(10, 1))

    # Convolutions on the frames on the screen
    # layer1 = layers.Conv2D(32, 8, strides=4, activation="relu")(inputs)
    # layer2 = layers.Conv2D(64, 4, strides=2, activation="relu")(layer1)
    # layer3 = layers.Conv2D(64, 3, strides=1, activation="relu")(layer2)

    layer1 = layers.Flatten()(inputs)

    layer2 = layers.Dense(20, activation="relu")(layer1)
    action = layers.Dense(num_actions, activation="linear")(layer2)

    return keras.Model(inputs=inputs, outputs=action)


# The first model makes the predictions for Q-values which are used to
# make a action.
model = create_q_model()
# Build a target model for the prediction of future rewards.
# The weights of a target model get updated every 10000 steps thus when the
# loss between the Q-values is calculated the target Q-value is stable.
model_target = create_q_model()

# In the Deepmind paper they use RMSProp however then Adam optimizer
# improves training time
optimizer = keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)

# outcome rewards
rewards = {
    'win': 10,
    'lose': -10,
    'tie': 5,
    'move': 0
}

# Experience replay buffers
buffers = {
    'action_history': [],
    'state_history': [],
    'state_next_history': [],
    'rewards_history': [],
    'done_history': []
}

running_reward = 0
epoch_count = 0
# Number of frames to take random action and observe output
epsilon_random_games = 2000
# Number of frames for exploration
epsilon_greedy_games = 1000.0
max_epochs = 50
# Maximum replay length
# Note: The Deepmind paper suggests 1000000 however this causes memory issues
buffer_size = 10000
# # Train the model after 4 actions
# update_after_actions = 4
# How often to update the target network
update_target_network = 2000
# Using huber loss for stability
loss_function = keras.losses.Huber()

game_count = 0
for epoch in range(max_epochs):
    losses = []
    
    print(f"*** EPOCH {epoch} ***")
    pbar = tqdm(range(update_target_network))
    for i in pbar:
        rolling_count = min(100, len(losses))
        pbar.set_description(f'loss={0 if not losses else np.mean(losses[-rolling_count:]):.3f}')
        game = TicTacToe()
        game_reward = 0
        if game_count < epsilon_random_games:
            player1 = DeepQPlayer(model, rewards, buffers, buffer_size, epsilon=1, name=f"Bot {game_count}a")
            player2 = DeepQPlayer(model, rewards, buffers, buffer_size, epsilon=1, name=f"Bot {game_count}b")
            game.play(player1, player2)
            epsilon_random_games += 1
        else:
            player1 = DeepQPlayer(model, rewards, buffers, buffer_size, epsilon=epsilon, name=f"Bot {game_count}a")
            player2 = DeepQPlayer(model, rewards, buffers, buffer_size, epsilon=epsilon, name=f"Bot {game_count}b")
            game.play(player1, player2)
            epsilon_greedy_games += 1
        game_count += 1

        # Decay probability of taking random action
        epsilon = max(epsilon - epsilon_interval / (max_epochs * update_target_network), epsilon_min)

        if len(buffers['done_history']) > batch_size:

            # Get indices of samples for replay buffers
            indices = np.random.choice(range(len(buffers['done_history'])), size=batch_size)

            # Using list comprehension to sample from replay buffer
            state_sample = np.array([buffers['state_history'][i] for i in indices])
            state_next_sample = np.array([buffers['state_next_history'][i] for i in indices])
            rewards_sample = [buffers['rewards_history'][i] for i in indices]
            action_sample = [buffers['action_history'][i] for i in indices]
            done_sample = tf.convert_to_tensor(
                [float(buffers['done_history'][i]) for i in indices]
            )            

            # Build the updated Q-values for the sampled future states
            # Use the target model for stability
            future_rewards = model_target.predict(state_next_sample, verbose=0)
            # Q value = reward + discount factor * expected future reward
            updated_q_values = rewards_sample + gamma * tf.reduce_max(
                future_rewards, axis=1
            )

            # If final frame set the last value to -1
            updated_q_values = updated_q_values * (1 - done_sample) - done_sample

            # Create a mask so we only calculate loss on the updated Q-values
            masks = tf.one_hot(action_sample, num_actions)

            with tf.GradientTape() as tape:
                # Train the model on the states and updated Q-values
                q_values = model(state_sample)

                # Apply the masks to the Q-values to get the Q-value for action taken
                q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                # Calculate loss between new Q-value and old Q-value
                loss = loss_function(updated_q_values, q_action)
                losses.append(loss.numpy())

            # Backpropagation
            grads = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(grads, model.trainable_variables))

    # update the the target network with new weights
    model_target.set_weights(model.get_weights())
    # Log details
    print(f"Avg Loss={np.mean(losses):.5f}, epsilon={epsilon:.2f}\n")
    epoch_count += 1
    # template = "running reward: {:.2f} at game {}, frame count {}"
    # print(template.format(running_reward, game_count, frame_count))

game = TicTacToe()
player1 = HumanPlayer()
player2 = DeepQPlayer(model, rewards, buffers, buffer_size, 0, name="Deep Q Bot", delay=1)
game.play(player1, player2, -1, True)