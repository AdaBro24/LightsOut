LightsOut Game
=========================

Python implementation of the Lights Out puzzle using tkinter GUI and search strategies.

This repository contains:

- `main.py` — launch point for the application.
- `gui.py` — the GUI logic
- `board.py` — board data structure and helpers.
- `search_strategies/` — package with search algorithms:
  - `uninformed/`: `bfs.py`, `dfs.py`, `iterative_deepening.py`, `ufc.py` (uniform-cost)
  - `heuristic/`: `astar.py`, `greedy.py` (different heuristic functions can be found inside "astar.py")
- `utils/` — helpers:
  - `io_utils.py`, (I/O)
  - `perf.py` (performance)
- `example.txt` — an example of a loadable board file.

Prerequisites
-------------
- Python 3.8+
- `tkinter` for the GUI. On many Linux distributions you need the system package (e.g. `sudo apt install python3-tk`).


Run 
---------
Start the GUI from the project root:

```bash
python3 main.py
```

- If `tkinter` is available the graphical window will open.
- If `tkinter` is missing, the program will not launch.

File format for board input
---------------------------
Boards are plain text files. Each non-empty line represents a board row. Values must be whitespace-separated 0 or 1 digits.

Example (3x3):

```
1 0 1
0 1 0
1 0 1
```

Place such a file anywhere and use the GUI "Load" button (or call loader functions) to load it.

Bulk-run / Save results
-----------------------
When you load a board using the GUI, the app will run a set of solvers over the loaded board and write a combined results file next to the input. The results file contains: which solvers ran, whether they found a solution, elapsed time, and peak Python memory usage measured by `tracemalloc`.


Heuristics and algorithms
-------------------------
Available heuristics (used by A* / greedy):
- `default_heuristic` — simple lights count
- `chase_lights_heuristic` — greedy row-chasing lower bound
- `isolated_lights_heuristic` — counts isolated lit cells
- `gf2_heuristic` — small GF(2) Gaussian elimination-based estimate (falls back to cheap heuristics if too expensive)

Solvers available under `search_strategies`:
- Uninformed: `bfs`, `dfs`, `iterative_deepening`, `ufc` (uniform-cost).
- Heuristic: `astar`, `weighted_astar`, `greedy`.
