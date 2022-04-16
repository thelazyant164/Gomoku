# Gomoku
- Gomoku.py: using metadata to calculate best move of each turn instead of a minimax algorithm, allowing your match to be lengthy and enjoyable without you being absolutely demolished.
- Gomoku_minimax.py: using metadata to evaluate value of game at each board state, then utilizing minimax algorithm to calculate several moves ahead

Features:
- There are several customization options to pick from: difficulty, board dimension, win condition, your mark...
- Due to time complexity, experimental customizations for maxDepthSearch is not encouraged, but on more capable hardware this can be increased to improve bot's predictions at the cost of performance

Achievements:
- Certified Tic-tac-toe (traditional Gomoku played on a 3x3 grid) champion
(in Tic-tac-toe, maxDepthSearch is set to 10 to ensure 100% game tree coverage; only plausible on this smallest board dimension due to relatively small possibilities of moves)

Heuristics:
- All recursions are implemented tail-recursively; only currently active stacks take up memory during runtime. Once an iteration of a recursion returns, it is pushed from stack and its return values are passed along to the next recursion call
=> Effectively, this means OS' built-in recursion depth limit is overridden, and function calls can recurse indefinitely
- When multiple moves are evaluated with the same score, only the first one is automatically saved, pruning the rest
- Evaluation of each node's value is skipped when node only has one child to inherit from
- First move of every game is either set randomly (for larger boards) or in the centre; recursive evaluation is not neccessary at this stage of the game
- maxDepthSearch increases as the game progresses to accurately reflect how a match climbs in intensity; each mistakes made further along the way has a bigger impact on the overall outcome of the match

Limitations:
- Evaluation function lacking efficiency in evaluating risks and opportunities for multi-directional streaks and non-continuous streaks
- Several heuristics and alpha-beta pruning have been applied to optimize performance, but this could be further improved upon
- Time complexity of minimax algorithm is exponentially large (O(n) = b^m where m is the maxDepthSearch/number of moves to forecast ahead, b is the branching factor which is virtually the remaining area of the playing board)
- Memory overflow is a possibility with large enough maxDepthSearch (due to certain lists being passed along recursive calls used to keep track of current contextual state, thus can't be pruned and incrementally grows in size with each recursion)
- Can only take manual coordinate input at this stage (can be cumbersome)
- Only limit to 26x26 board at maximum (due to each column being indicated by a letter in the alphabet)

Modules:
- "Gomoku.py" is the original source code, written in Python.
- "Gomoku_minimax.py" is the minimax implementation, utilizing the original evaluation function to evaluate non-ending terminal nodes - requires "tail_recursion.py" to run and should automatically generate a "_pycache_" directory when run (16/04/2022)

Possible future update:
- Rework evaluation function to better evaluate risks and opportunities for multi-directional streaks and non-continuous streaks
- Rework contextual tracking system to allow for dynamic pruning, alleviating memory allocation
- Dynamic maxDepthSearch, implementing a real-time estimation system to determine how much time the game tree would take to fully develop from the board's current state, then self-modify maxDepthSearch to ensure time transpired between each bot's move doesn't surpass pre-defined threshold
- More precise heuristics and effectual alpha-beta pruning to reduce recursion calls and improve performance
- A GUI interface that allows for more intuitive click-to-select option
- Support for even bigger playing board