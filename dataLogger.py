import melee
import csv
import os
from pathlib import Path

# Similar code to melee.Logger()

fieldnames = ['Opponent x', 'Opponent y', 'AI x', 'AI y',
              'Opponent Facing', 'AI Facing',
              'Opponent Action', 'AI Action',
              'Opponent Action Frame', 'AI Action Frame',
              'Opponent Jumps Left', 'AI Jumps Left',
              'Opponent Stock', 'AI Stock',
              'Opponent Percent', 'AI Percent']


def normalize_value(x, x_min, x_max):
    """
    Normalizes float or integer value between [-1, 1]
    :param x:       value to be normalized
    :param x_min:   minimum value
    :param x_max:   maximum value
    :return:        normalized value
    """
    # TODO: We can save range and mid values initialize to save computation time.
    x_range = x_max - x_min
    x_mid = (x_max + x_min)/2

    x_normalized = 2 * (x - x_mid) / x_range
    return x_normalized


def normalize_bool(x):
    """
    Normalizes boolean value between [-1, 1]
    :param x:       boolean value to be normalized
    :return:        normalized value
    """
    x_normalized = 1 if x else -1
    return x_normalized

class DataLogger:
    def __init__(self, ai_port=1, opponent_port=2):
        # Save port of AI and opponent
        self.ai_port = ai_port
        self.opponent_port = opponent_port

        # Ensure directory exists.
        if not os.path.exists(Path("Logs")):
            os.makedirs(Path("Logs"))

        # Open CSV file.
        self.csvfile = open("Logs/data.csv", 'w', newline='')

        # Initialize CSV writer.
        self.writer = csv.DictWriter(self.csvfile, fieldnames=fieldnames, extrasaction='ignore')
        self.current_row = dict()
        self.rows = []
        self.filename = self.csvfile.name

    def __del__(self):
        # Close CSV file
        if self.csvfile:
            self.csvfile.close()

    def log(self, column, contents, concat=False):
        """Write 'contents' to the log at given 'column'

        Args:
            column (str): The column to write the log message at
            contents (str): The thing to write to the log
            concat (bool): Should we concatenate the contents to the existing log at that column
                (or replace it)
        """
        # Should subsequent logs be cumulative?
        if concat:
            if column in self.current_row:
                self.current_row[column] += contents
            else:
                self.current_row[column] = contents
        else:
            self.current_row[column] = contents

    def logframe(self, gamestate):
        """Log any common per-frame things

        Args:
            gamestate (gamestate.GameState): A gamestate object to log
        """
        # Note: Assumes 2 players.
        ai_state = None
        opponent_state = None

        for port_number, player_state in gamestate.player.items():
            if port_number == self.ai_port:
                ai_state = player_state
            elif port_number == self.opponent_port:
                opponent_state = player_state

        if not ai_state and not opponent_state:
            # Not enough players found.
            return

        # Current actions and positions
        self.log('Opponent x', opponent_state.x)
        self.log('Opponent y', opponent_state.y)
        self.log('AI x', ai_state.x)
        self.log('AI y', ai_state.y)

        self.log('Opponent Facing', int(opponent_state.facing))
        self.log('AI Facing', int(ai_state.facing))

        self.log('Opponent Action', int(opponent_state.action.value))
        self.log('AI Action', int(ai_state.action.value))

        self.log('Opponent Action Frame', int(opponent_state.action_frame))
        self.log('AI Action Frame', int(ai_state.action_frame))

        self.log('Opponent Jumps Left', int(opponent_state.jumps_left))
        self.log('AI Jumps Left', int(ai_state.jumps_left))

        self.log('Opponent Stock', int(opponent_state.stock))
        self.log('AI Stock', int(ai_state.stock))

        self.log('Opponent Percent', int(opponent_state.percent))
        self.log('AI Percent', int(ai_state.percent))

        # TODO: Possibly add projectiles as input. However, there may be multiple entities.
        # gamestate.projectiles
        #   owner, subtype, x, x_speed, y, y_speed

        # TODO: Possibly add randall position for Yoshi's story as input.

        # TODO: Need a way to handle Sheik/Zelda transformation.

        # # Normalize inputs for neural network.
        # self.normalize_inputs(gamestate)

    def normalize_inputs(self, gamestate):
        """
        Normalizes inputs for neural network.
        :param gamestate (gamestate.GameState): A gamestate object to log
        """
        # Normalize position values between [-1, 1]
        x_min, x_max, y_max, y_min = melee.stages.BLASTZONES[gamestate.stage]

        self.current_row['Opponent x'] = normalize_value(self.current_row['Opponent x'], x_min, x_max)
        self.current_row['Opponent y'] = normalize_value(self.current_row['Opponent y'], y_min, y_max)
        self.current_row['AI x'] = normalize_value(self.current_row['Opponent x'], x_min, x_max)
        self.current_row['AI y'] = normalize_value(self.current_row['Opponent y'], y_min, y_max)

        assert((self.current_row['Opponent y']) <= 1 and (self.current_row['Opponent y'] >= -1))

        self.current_row['Opponent Facing'] = normalize_bool(['Opponent Facing'])
        self.current_row['AI Facing'] = normalize_bool(['AI Facing'])

        # TODO: Possibly use a different encoding. Leave as default for now.
        # self.current_row['Opponent Action']
        # self.current_row['AI Action']
        #
        # self.current_row['Opponent Action Frame']
        # self.current_row['AI Action Frame']
        #
        # self.current_row['Opponent Jumps Left']
        # self.current_row['AI Jumps Left']
        #
        # self.current_row['Opponent Stock']
        # self.current_row['AI Stock']
        #
        # self.current_row['Opponent Percent']
        # self.current_row['AI Percent']


    def writeframe(self):
        """Write the current frame to the log and move to a new frame"""
        self.rows.append(self.current_row)
        self.current_row = dict()

    def writelog(self):
        """Write the log to file """
        self.writer.writerows(self.rows)

        # Close csv file
        self.csvfile.close()


