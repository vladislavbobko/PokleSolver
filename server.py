from flask import Flask, request
from flask_cors import CORS

# from scripts.PokleGame.solver import Poklesolver
from src.PokleSolver import PokleSolver

app = Flask(__name__)
CORS(app, supports_credentials=True)

# decoding table for colors
DECODE = {'grey': '!', 'darkgreen': '', 'gold': '?'}
DEF_FILE = 'solutions.txt'

@app.route('/solve', methods=['POST'])
def solve():
    game_string = request.json['gameString']

    solver = PokleSolver(hands=None, order=None, game_string=game_string)
    solver.solve(cores=8)
    solver.write_solutions_to_file(DEF_FILE)

    return ''

@app.route('/filter', methods=['POST'])
def filter():
    # prepare data
    data = request.json
    colors, guess = [DECODE[c] for c in data['colors']], data['guess'].split(' ')
    print ( f'   -> received data: {data}')

    # zip them together
    formatted = [ f'{c}{g}' for c, g in list ( zip ( colors, guess ) ) ]
    flop, turn, river = ' '.join(formatted[0:3]), formatted[3], formatted[4]

    solver = PokleSolver()
    solver.filter(DEF_FILE, flop, turn, river)
    solver.write_solutions_to_file(DEF_FILE)

    return '{}'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
