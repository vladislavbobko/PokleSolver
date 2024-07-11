import argparse

from src.PokleSolver import PokleSolver

# getting config from selenium dynamic load
def selenium_get_config ():
    from undetected_chromedriver import Chrome, ChromeOptions
    script = r"return localStorage [ 'gameString' ]"

    # make sure it starts without gui
    opts = ChromeOptions()
    opts.add_argument('--headless')
    opts.add_argument('--disable-gpu')

    # set options to prevent Chrome from showing the "Chrome is being controlled by automated test software" notification
    opts.add_argument('--disable-logging')
    opts.add_argument('--disable-extensions')
    opts.add_argument('--disable-infobars')
    opts.add_argument('--disable-blink-features=AutomationControlled')

    # start chrome and get the page
    chrome = Chrome(options=opts)
    chrome.get ( "https://poklegame.com")

    # get the actual value
    game_string = chrome.execute_script ( script )
    print ( f" - successfully extracted the gamestring!")

    # close chrome and return
    chrome.quit()

    return game_string

# CLI usage of the PokleSolver
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("action", help="action to perform, either 'solve' or 'filter'", choices=["solve", "filter"])

    # input for solvings
    parser.add_argument("--hands", help="hands from gamestring", required=False)
    parser.add_argument("--order", help="player positions", required=False)
    parser.add_argument("--game_string", help="gameString from Pokle", required=False)
    parser.add_argument("--use_selenium", action='store_true', help="use selenium to get gameString", required=False)

    # input for filtering
    parser.add_argument("--input",  type=str, nargs='?', default='solutions.txt', help="file containing generated solutions", )
    parser.add_argument("--output", type=str, nargs='?', default='solutions.txt', help="file to write generated solutions",   )

    # flop/turn/river inputs
    parser.add_argument("--flop", help="file to write generated solutions", required=False)
    parser.add_argument("--turn", help="file to write generated solutions", required=False)
    parser.add_argument("--river", help="file to write generated solutions", required=False)

    # parallelization
    parser.add_argument("--cores", help="file to write generated solutions", type=int, required=False, const=1, nargs='?')
    
    args = parser.parse_args()

    if args.action == "solve":
        if args.use_selenium:
            solver = PokleSolver(hands=None, order=None, game_string=selenium_get_config())
        elif args.game_string:
            solver = PokleSolver(hands=None, order=None, game_string=args.game_string)
        elif args.hands or args.order:
            if not args.hands or not args.order:
                print ( "[!] both --hands and --order are required for solving" )
                exit (1)
            solver = PokleSolver(hands=args.hands, order=args.order, game_string=None)
        else:
            print ( f"[!] invalid option provided!")

        solver.solve(args.cores if args.cores else 1)

    elif args.action == "filter":
        solver = PokleSolver()
        if not args.input:
            print ( "[!] --input is required for filtering!" )
            exit (1)

        solver.filter(args.input, args.flop, args.turn, args.river)

    if args.output:
        solver.write_solutions_to_file(args.output)
