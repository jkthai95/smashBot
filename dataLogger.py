import melee
import csv
import os


class DataLogger(melee.Logger):
    def __init__(self):
        super().__init__()
        # Delete old CSV file created by super class
        # TODO: May be better to just our own class instead of doing this.
        self.writer = None
        self.csvfile.close()
        os.remove(self.csvfile.name)
        fieldnames = ['Opponent x', 'Opponent y', 'AI x', 'AI y', 'Opponent Facing', 'AI Facing',
                      'Opponent Action', 'AI Action', 'Opponent Action Frame', 'AI Action Frame',
                      'Opponent Jumps Left', 'AI Jumps Left', 'Opponent Stock', 'AI Stock',
                      'Opponent Percent', 'AI Percent']
                      # ,'AI Button A', 'AI Button B', 'AI R Shoulder', 'AI C Stick X', 'AI C Stick Y', 'AI Main Stick X', 'AI Main Stick Y']
        self.csvfile = open("Logs/data.csv", 'w')
        self.writer = csv.DictWriter(self.csvfile, fieldnames=fieldnames, extrasaction='ignore')
        self.filename = self.csvfile.name

    def logframe(self, gamestate):
        """Log any common per-frame things

        Args:
            gamestate (gamestate.GameState): A gamestate object to log
        """
        opponent_state = None
        ai_state = None
        count = 0
        for i, player in gamestate.player.items():  # TODO: This seems to assume 1st player is AI.
            if count == 0:
                ai_state = player
                count += 1
            elif count == 1:
                opponent_state = player
                count += 1

        if not opponent_state or not ai_state:
            return

        # Current actions and positions
        self.log('Opponent x', str(opponent_state.x))
        self.log('Opponent y', str(opponent_state.y))
        self.log('AI x', str(ai_state.x))
        self.log('AI y', str(ai_state.y))
        self.log('Opponent Facing', str(opponent_state.facing))
        self.log('AI Facing', str(ai_state.facing))
        self.log('Opponent Action', str(opponent_state.action))
        self.log('AI Action', str(ai_state.action))
        self.log('Opponent Action Frame', str(opponent_state.action_frame))
        self.log('AI Action Frame', str(ai_state.action_frame))
        self.log('Opponent Jumps Left', str(opponent_state.jumps_left))
        self.log('AI Jumps Left', str(ai_state.jumps_left))
        self.log('Opponent Stock', str(opponent_state.stock))
        self.log('AI Stock', str(ai_state.stock))
        self.log('Opponent Percent', str(opponent_state.percent))
        self.log('AI Percent', str(ai_state.percent))

        # # AI Inputs
        # ai_controller_state = ai_state.controller_state
        # self.log('AI Button A', str(ai_controller_state.button[melee.Button.BUTTON_A]))
        # self.log('AI Button B', str(ai_controller_state.button[melee.Button.BUTTON_B]))
        # self.log('AI R Shoulder', str(ai_controller_state.r_shoulder))
        # self.log('AI C Stick X', str(ai_controller_state.c_stick[0]))
        # self.log('AI C Stick Y', str(ai_controller_state.c_stick[1]))
        # self.log('AI Main Stick X', str(ai_controller_state.main_stick[0]))
        # self.log('AI Main Stick Y', str(ai_controller_state.main_stick[1]))