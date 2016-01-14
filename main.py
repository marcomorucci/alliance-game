from game import Game, GameMove
from gameGraph import GameGraph, GameNode, EmptyNode
from player import Player, Unit, RandomPlayer, ShortHorizonPlayer
import sys
import graphics
import numpy as np
from progressbar import ProgressBar, Bar, Percentage
from csv import DictWriter
from sklearn.linear_model import LogisticRegression
from pandas import DataFrame


def main(argv):

    weights = {"unit_weight": 1, "node_weight": 1, "occ_weight": 1, "occ_new_weight": 1,
               "n_enemies_weight": 1, "enemy_occ_nodes_weight": 1, "enemy_unit_weight": 1,
               "empty_node_weight": 1, "attacker_weight": 1, "defender_weight": 1,
               "occ_attacker_weight": 1, "occ_defender_weight": 1, "enemy_occ_attacker_weight": 1,
               "enemy_occ_defender_weight": 1}

    vars = weights.keys()
    vars.append("won")
    data = []
    n_win = 0
    with open("data.csv", "wb") as f:
        w = DictWriter(f, vars)
        w.writeheader()
        for g in range(100):

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

            print "game %d, %d winners so far" % (g, n_win)
            r = 0
            win = None
            while win is None and r < 100:
                print r
                win = game.play_round()
                r += 1
            print "Winner:", win

            if win is not None:
                n_win += 1
                for p in players:
                    for l in p.weights:
                        l["won"] = 1 if win == p.id else 0
                        w.writerow(l)
                        data.append(l)

    weights = compute_weights(DataFrame(data), weights.keys(), "won")
    print "final weights", weights


def compute_weights(data, x_names, y_names):
    m = LogisticRegression()
    m.fit(data[x_names], data[y_names])
    return {x_names[i]: m.coef_[0][i] for i in range(len(x_names))}

                        
if __name__ == "__main__":
    main(sys.argv[1:])