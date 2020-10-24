import argparse
import melee
import sys


def check_port(value):
    """
    Checks if port number is valid. Must be between [1, 4].
    :param value: Input port number.
    :return: Output port number.
    """
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4:
        raise argparse.ArgumentTypeError("%s is an invalid controller port. \
                                         Must be 1, 2, 3, or 4." % value)
    return ivalue


def parse_arguments():
    """
    Parses arguments.
    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description='Simple SSBM Bot trained using Reinforcement Learning.')
    parser.add_argument('--port', '-p', type=check_port,
                        help='The controller port (1-4) your AI will play on',
                        default=2)
    parser.add_argument('--opponent', '-o', type=check_port,
                        help='The controller port (1-4) the opponent will play on',
                        default=1)
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Debug mode. Creates a CSV of all game states')
    parser.add_argument('--framerecord', '-r', default=False, action='store_true',
                        help='(DEVELOPMENT ONLY) Records frame data from the match,' \
                             'stores into framedata.csv.')
    parser.add_argument('--address', '-a', default="127.0.0.1",
                        help='IP address of Slippi/Wii')
    parser.add_argument('--dolphin_executable_path', '-e', default=None,
                        help='The directory where dolphin is')
    parser.add_argument('--connect_code', '-t', default="",
                        help='Direct connect code to connect to in Slippi Online')
    args = parser.parse_args()
    return args


def main():
    # Parse arguments.
    args = parse_arguments()

    # Create logger object if we are debugging
    log = None
    if args.debug:
        log = melee.Logger()

    # This frame data object contains lots of helper functions and values for looking up
    #   various Melee stats, hitboxes, and physics calculations
    framedata = melee.FrameData(args.framerecord)

    # Create console object for melee. Used to interface with melee.
    console = melee.Console(path=args.dolphin_executable_path,
                            slippi_address=args.address,
                            slippi_port=51441,
                            blocking_input=False,
                            polling_mode=False,
                            logger=log)

    # Dolphin has an optional mode to not render the game's visuals
    #   This is useful for BotvBot matches
    console.render = True

    # Create our Controller object
    #   The controller is the second primary object your bot will interact with
    #   Your controller is your way of sending button presses to the game, whether
    #   virtual or physical.
    controller = melee.Controller(console=console,
                                  port=args.port,
                                  type=melee.ControllerType.STANDARD)

    # Run console.
    console.run()

    # Connect to console.
    print("Connecting to console...")
    if not console.connect():
        print("ERROR: Failed to connect to the console.")
        sys.exit(-1)
    print("Console connected")

    # Plug in our controller.
    print("Connecting controller to console...")
    if not controller.connect():
        print("ERROR: Failed to connect the controller.")
        sys.exit(-1)
    print("Controller connected")

    # Main loop.
    while True:
        # "step" to the next frame
        gamestate = console.step()
        if gamestate is None:
            continue

        # The console object keeps track of how long your bot is taking to process frames
        #   And can warn you if it's taking too long
        if console.processingtime * 1000 > 12:
            print("WARNING: Last frame took " + str(console.processingtime * 1000) + "ms to process.")

        # What menu are we in?
        if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:

            # Slippi Online matches assign you a random port once you're in game that's different
            #   than the one you're physically plugged into. This helper will autodiscover what
            #   port we actually are.
            discovered_port = args.port
            if args.connect_code != "":
                discovered_port = melee.gamestate.port_detector(gamestate, melee.Character.FOX, 0)
                print(discovered_port)
            if discovered_port > 0:
                if args.framerecord:
                    framedata._record_frame(gamestate)
                # NOTE: This is where your AI does all of its stuff!
                # This line will get hit once per frame, so here is where you read
                #   in the gamestate and decide what buttons to push on the controller
                if args.framerecord:
                    melee.techskill.upsmashes(ai_state=gamestate.player[discovered_port], controller=controller)
                else:
                    melee.techskill.multishine(ai_state=gamestate.player[discovered_port], controller=controller)
            else:
                # If the discovered port was unsure, reroll our costume for next time
                costume = random.randint(0, 4)
        elif gamestate.menu_state == melee.Menu.CHARACTER_SELECT:
            melee.menuhelper.MenuHelper.menu_helper_simple(gamestate,
                                                           controller,
                                                           args.port,
                                                           melee.enums.Character.FOX,
                                                           melee.enums.Stage.FINAL_DESTINATION,
                                                           args.connect_code,
                                                           costume=0,
                                                           autostart=args.connect_code != "",
                                                           swag=True)
        if log:
            log.logframe(gamestate)
            log.writeframe()

if __name__ == '__main__':
    main()





