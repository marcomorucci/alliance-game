from game import Game
from gameGraph import GameGraph, GameNode, EmptyNode
from player import Player, Unit, RandomPlayer, ShortHorizonPlayer, HumanInteractionUnit, HumanPlayer
import sys
import graphics


def test_sh_player():

    weights = {"unit_weight": 1.242, "node_weight": -0.4971, "occ_weight": 0, "occ_new_weight": 0.05953,
               "n_enemies_weight": 0.2306, "enemy_occ_nodes_weight": -1.126, "enemy_unit_weight": -0.2431,
               "empty_node_weight": -0.7042, "attacker_weight": -0.3131, "defender_weight": 0.06549,
               "occ_attacker_weight": -0.2173, "occ_defender_weight": 0.4239, "enemy_occ_attacker_weight": 0.3953,
               "enemy_occ_defender_weight": -0.02868}

            
    nodes = [GameNode(0, [], [1, 2]),
             GameNode(1, [], [0, 2]),
             GameNode(2, [], [0, 1, 3]),
             GameNode(3, [], [2, 4, 5]),
             GameNode(4, [], [3, 5]),
             GameNode(5, [], [3, 4])]

    players = [ShortHorizonPlayer(0, [Unit(0, nodes[0])], [nodes[0]], nodes[0], **weights),
               ShortHorizonPlayer(1, [Unit(1, nodes[1])], [nodes[1]], nodes[1], **weights),
               ShortHorizonPlayer(2, [Unit(2, nodes[4])], [nodes[4]], nodes[4], **weights),
               ShortHorizonPlayer(3, [Unit(3, nodes[5])], [nodes[5]], nodes[5], **weights)]

    nodes[0].add_unit(players[0].units[0])
    nodes[1].add_unit(players[1].units[0])
    nodes[4].add_unit(players[2].units[0])
    nodes[5].add_unit(players[3].units[0])
    
    graph = GameGraph(nodes)
    
    game = Game(players, graph)

    game.update_state([], False)

    def next_round(event):
        win = game.play_round()
        if win is None:
            graphics.draw(f, w, l, game.state)
        else:
            graphics.draw_winner(w, win)
    
    f, w, l = graphics.setup(game.state, next_round)
    
    graphics.draw(f, w, l, game.state)
    graphics.show()

    
def test_human_player():
            
    nodes = [GameNode(0, [], [1, 2]),
             GameNode(1, [], [0, 2]),
             GameNode(2, [], [0, 1, 3]),
             GameNode(3, [], [2, 4, 5]),
             GameNode(4, [], [3, 5]),
             GameNode(5, [], [3, 4])]

    players = [HumanPlayer(0, [HumanInteractionUnit(0, nodes[0])], [nodes[0]], nodes[0]),
               HumanPlayer(1, [HumanInteractionUnit(1, nodes[1])], [nodes[1]], nodes[1]),
               HumanPlayer(2, [HumanInteractionUnit(2, nodes[4])], [nodes[4]], nodes[4]),
               HumanPlayer(3, [HumanInteractionUnit(3, nodes[5])], [nodes[5]], nodes[5])]

    nodes[0].add_unit(players[0].units[0])
    nodes[1].add_unit(players[1].units[0])
    nodes[4].add_unit(players[2].units[0])
    nodes[5].add_unit(players[3].units[0])
    
    graph = GameGraph(nodes)
    
    game = Game(players, graph)

    game.update_state([], False)

    def next_round(event):
        win = game.play_round()
        if win is None:
            graphics.draw(f, w, l, game.state)
        else:
            graphics.draw_winner(w, win)
    
    f, w, l = graphics.setup(game.state, next_round)

    for p in players:
        p.canvas = w
    
    graphics.draw(f, w, l, game.state)
    graphics.show()


def main(argv):

    if len(argv) > 0 and argv[0] == "human":
        test_human_player()
    else:
        test_sh_player()
    
    
if __name__ == "__main__":
    main(sys.argv[1:])
