# PySampleProject

Simple bruteforce solver for [poklegame.com](https://poklegame.com).

## Usage

### Solving

- cli: `python3 ./cli.py solve --use_selenium --cores 8` (fetching gamestring via Selenium)
- server: sending POST to `http://localhost:5000/solve` with JSON payload as `{"gameString": <>}`

### Filtering

Prefixes:
- gray card: `!`
- yellow: `?`
- green: NONE

In below example, in the flop we have green 6clubs, 3spades and gray 5hearts.

- cli: `python3 ./cli.py filter --flop '6c 3s !5h' --turn '!Kh' --river '?Jd'`
- server: send POST to `http://localhost:5000/filter` with JSON payload as: `{"colors": ["darkgreen", "darkgreen", "grey", "grey", "gold"], "guess": "6c 3s 5h kh jd"}`
