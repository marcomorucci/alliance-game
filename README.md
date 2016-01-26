# alliance-game

Here is the code for the alliance game, and a player that simply evaluates some utility parameters before choosing a move.

##NOTE:
There is still **A LOT** of work to do here, code must be cleaned up and a lot of hastily-written pieces must be rewritten with some better software development practices. 

##Running it
The best idea so far is to do

	python test.py

to launch a simulation with 4 ShortHorizonPlayers. The simulation advances 1 round after each keypress.
If you want to change the parameters you can edit the test.py, sorry but it's a mess as of now. 


The graphics are based on tkinter and can be interpreted as follows:

* White Nodes: not owned by any player
* Colored nodes: owned by a player
* Small colored circles: units, each colored according to player that owns it.
* Blue line: unit is defending target node
* Red line: unit is attacking target node


##The Game
I tried to keep it as similar to what is described in the chapter, I did have to make some implementation decisions.
Here is a list (not exhaustive) of choices that I had to make:

* The game state is update after each player move but **not** after each unit move.
* Players that lose all nodes and all units are eliminated from the game.
* Units play attack or support on a *node* rather than a *unit*
* Units that lose after an attack are **randomly** reassigned to a free connected node or destroyed if there are no nodes available.
* After a successful attack on a node, the node remains unoccupied and players have to explicitly move onto it to conquer it.


##The Players
There are 2 types of players included here:

* RandomPlayer: chooses a random move from all legal moves available.
* ShortHorizonPlayer: Chooses the move with the immediate highest utility at the next state.

### ShortHorizonPlayer
This player is an initial implementation of a heuristic-based player. I really just wanted to use it as a skeleton for a player that
also did some kind of search but I haven't gotten that far yet. I chose a number of features to evaluate intermediate utilities after each possible move. These are:

* unit: How many units will I have after I make this move.
* node: How many nodes will I own after I make this move.
* occ: How many nodes will I occupy after I make this move. 
* occ_new: How many nodes will I occupy that I don't now after I make this move.
* n_enemies: How many enemies will there be left after I make this move.
* enemy_occ_nodes: How many nodes will my enemies occupy after I make this move.
* enemy_unit: How many units will my enemies have left after I make this move.
* empty_node: How many empty nodes will there be on the board after I make this move.
* attacker: How many enemy units will be attacking nodes owned by me after I make this move.
* defender: How many units will be defending nodes owned by me after I make this move.
* occ_attacker: How many enemy units will be attacking nodes occupied by me after I make this move.
* occ_defender: How many units will be defending nodes occupied by me.
* enemy_occ_attacker: How many units will be attacking nodes owned by my enemies after I make this move.
* enemy_occ_defender: How many units will be defending nodes owned by my enemies after I make this move.

These are in no way exhaustive of all possible and useful features and are just some ones I could come up with off the top of my head to test the player.

There is a **weight** associated with each one of these utilities. I've left these weights at 1 initially, and then played some games
and regressed features on outcomes to calculate weights. More on this in the results section.

One thing worth noting is how the player works: it simulates the game state after each move and evaluates the features on the simulated state, picking the move that yields the greatest utility. If more than 1 move set have max utility, one is picked at random.

###Some Results

I ran several iterations of games played at random and recorded feature values at each move played by each player. I then stored wether that game resulted in a win or a loss and ran a regression on the result. The dependent variable is a boolean for wether the game was won, the independents are feature weights. Below is a table of computed coefficients/weights. Some make sense, some less. 

Coefficient | Estimate | Std. Error  | z value | Pr(>z) 
---------------|--------------|--------------|-----------|--------
node_weight | -0.4971 |  0.121  |    -4.107  | 4.005e-05 
n_enemies_weight | 0.2306  |   0.05859   |   3.936  | 8.27e-05
enemy_occ_nodes_weight | -1.126  | 0.05936  | -18.97  | 2.943e-80
enemy_occ_defender_weight | -0.02868   |  0.0222    | -1.292   | 0.1964
defender_weight | 0.06549  |    0.1357  |   0.4826 |  0.6293
occ_new_weight |        0.05953 |     0.1923 |    0.3096 |  0.7569
enemy_occ_attacker_weight  | 0.3953  |  0.02399   |   16.48 |  5.319e-61
attacker_weight | -0.3131  |    0.2292  |   -1.366 |  0.172
enemy_unit_weight |     -0.2431  |   0.04761 |    -5.105  | 3.299e-07
unit_weight |   1.242  |     0.2035  |    6.102 |  1.045e-09
occ_attacker_weight |    -0.2173  |    0.2334  |   -0.9308  | 0.3519
occ_defender_weight |   0.4239  |    0.1348  |    3.146  | 0.001658
empty_node_weight |  -0.7042   |  0.05129  |   -13.73 |  6.851e-43


The players in the simulation in test.py are all initialized with these weights. 


##The interface

I tried to build this so that new classes of players could more or less be easily implemented. To write a new player the **Player** class must be inherited and the only requirement is that the **play** function is implemented. Below is a list of few things to keep in mind when working with this code to implement new players:

1. The **play** function takes a *Game* object as an imput and returns a list of *GameMove* object, one for each unit.
2. The **GameMove** object consists of a unit, an origin and destination node (which can be the same), an action, either "attack", "support", "nothing"; and a target node, which can be EmptyNode() if the action is "nothing".
3. The **Game** class offers a *get_legal_moves* helper function that returns all legal GameMoves for the player at that turn.
4. The **Game** class also offers a *simulate* function that returns a simulated game state, useful for expanding the game tree/evaluating moves.
5. The move list returned by *game.get_legal_moves*(player)* is made up of lists of moves for each unit, these must be combined into a list of possible combination by the player.
6. In general, the **Game** object holds references to all other objects in the program, making it (supposedly) easy to evaluate whichever features in present or simulated states. 


##Human Interaction

###TL,DR: it's broken and unfinished for now.

To launch it do:

	python test.py human

**N.B.** There is a problem with the move selection. If you shut the window before having clicked on complete move, the interpreter will keep running in the background until you pkill it. 

###TODO:

1. Fix board drawing so that it happens after each individual move. Now it only happens after **all** players have moved, which is fine for computer players but not for human ones.
- The best way of doing this is to create a HumanGame class that inherits from Game and changes some key things to better suit human players.
2. There is a timing issue with the play fcn for Human Players, It's fixed for the most part, but I can't get get the move summary menu to redraw after each selection. The problem has to do with tkinter's mainloop and waiting for player input in the game before returning the selected move. For now I do this with tkinter's wait_variable() fcn, which seems to work.
 - The other problem is that wait_variable won't exit until you click on complete move in the dialog. This has to change so that it also exits when the main application exits (window closed)
3. Generally make sure that the game behaves as it should given our definitions and the rules. I'm not 100% sure that it does.
5. Implement move data collection for human players.
4. There's probably more but this is all I could come up with for now.

The Human Interaction module is structured around 2 classes: HumanPlayer and HumanInteractionUnit. It's fair to say that the heavy lifting is done by the second one. Most of the work is GUI, so there are a lot of tkinter calls in both classes. They communicate with the graphics module in a very clumsy way, which should be refactored to ensure proper encapsulation.
