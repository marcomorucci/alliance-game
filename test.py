from game import Game, GameMove
from gameGraph import GameGraph, GameNode, EmptyNode
from player import Player, Unit, RandomPlayer, ShortHorizonPlayer
import sys
import graphics
import numpy as np


def test_game():

    nodes = [GameNode(0, [], [1, 2]),
             GameNode(1, [], [0, 2]),
             GameNode(2, [], [0, 1, 3]),
             GameNode(3, [], [2, 4, 5]),
             GameNode(4, [], [3, 5]),
             GameNode(5, [], [3, 4])]

    players = [Player(0, [Unit(0, nodes[0])], [nodes[0]], nodes[0]),
               Player(1, [Unit(1, nodes[1])], [nodes[1]], nodes[0]),
               Player(2, [Unit(2, nodes[4])], [nodes[4]], nodes[0]),
               Player(3, [Unit(3, nodes[5])], [nodes[5]], nodes[0])]

    nodes[0].add_unit(players[0].units[0])
    nodes[1].add_unit(players[1].units[0])
    nodes[4].add_unit(players[2].units[0])
    nodes[5].add_unit(players[3].units[0])
    
    graph = GameGraph(nodes)
    
    game = Game(players, graph)

    game.update_state([], False)
    
    
    
    print "Initial State"
    
    print game.state

    print "First Moves"

    moves = [GameMove(players[0].units[0], players[0].units[0].node, nodes[2], "nothing", EmptyNode()),
             GameMove(players[1].units[0], players[1].units[0].node, EmptyNode(), "attack", nodes[2])]
    game.update_state(moves, True)
    
    print game.state

    print "Second Move"

    moves = [GameMove(players[3].units[0], players[3].units[0].node, nodes[3], "attack", nodes[2])]
    game.update_state(moves, True)

    print game.state


def test_rounds():
    nodes = [GameNode(0, [], [1, 2]),
             GameNode(1, [], [0, 2]),
             GameNode(2, [], [0, 1, 3]),
             GameNode(3, [], [2, 4, 5]),
             GameNode(4, [], [3, 5]),
             GameNode(5, [], [3, 4])]

    players = [RandomPlayer(0, [Unit(0, nodes[0])], [nodes[0]], nodes[0]),
               RandomPlayer(1, [Unit(1, nodes[1])], [nodes[1]], nodes[0]),
               RandomPlayer(2, [Unit(2, nodes[4])], [nodes[4]], nodes[0]),
               RandomPlayer(3, [Unit(3, nodes[5])], [nodes[5]], nodes[0])]

    nodes[0].add_unit(players[0].units[0])
    nodes[1].add_unit(players[1].units[0])
    nodes[4].add_unit(players[2].units[0])
    nodes[5].add_unit(players[3].units[0])
    
    graph = GameGraph(nodes)
    
    game = Game(players, graph)

    game.update_state([], False)
    
    print "Initial State"
    print game.state
    game.state.graph.draw()
    
    for p in players:
        m = p.play(game)
        for i in m:
            print i
        game.update_state(m)
        
    print "First Move"
    print game.state

    
def test_draw():
    nodes = [GameNode(0, [], [1, 2]),
             GameNode(1, [], [0, 2]),
             GameNode(2, [], [0, 1, 3]),
             GameNode(3, [], [2, 4, 5]),
             GameNode(4, [], [3, 5]),
             GameNode(5, [], [3, 4])]

    players = [RandomPlayer(0, [Unit(0, nodes[0], action="attack", target=nodes[1]), Unit(0, nodes[0])], [nodes[0]], nodes[0]),
               RandomPlayer(1, [Unit(1, nodes[1]), Unit(1, nodes[1])], [nodes[1]], nodes[0]),
               RandomPlayer(2, [Unit(2, nodes[4]), Unit(2, nodes[4], action="support", target=nodes[5])], [nodes[4]], nodes[0]),
               RandomPlayer(3, [Unit(3, nodes[5]), Unit(3, nodes[5])], [nodes[5]], nodes[0])]

    nodes[0].add_unit(players[0].units[0])
    nodes[1].add_unit(players[1].units[0])
    nodes[4].add_unit(players[2].units[0])
    nodes[5].add_unit(players[3].units[0])
    
    nodes[0].add_unit(players[0].units[1])
    nodes[1].add_unit(players[1].units[1])
    nodes[4].add_unit(players[2].units[1])
    nodes[5].add_unit(players[3].units[1])
    
    graph = GameGraph(nodes)
    
    game = Game(players, graph)

    game.update_state([], False)

    w, l = graphics.setup(game.state)
    graphics.draw(w, l, game.state)
    graphics.show()
    

def test_random():
    nodes = [GameNode(0, [], [1, 2]),
             GameNode(1, [], [0, 2]),
             GameNode(2, [], [0, 1, 3]),
             GameNode(3, [], [2, 4, 5]),
             GameNode(4, [], [3, 5]),
             GameNode(5, [], [3, 4])]

    players = [RandomPlayer(0, [Unit(0, nodes[0])], [nodes[0]], nodes[0]),
               RandomPlayer(1, [Unit(1, nodes[1])], [nodes[1]], nodes[0]),
               RandomPlayer(2, [Unit(2, nodes[4])], [nodes[4]], nodes[0]),
               RandomPlayer(3, [Unit(3, nodes[5])], [nodes[5]], nodes[0])]

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


def test_simulation():
    nodes = [GameNode(0, [], [1, 2]),
             GameNode(1, [], [0, 2]),
             GameNode(2, [], [0, 1, 3]),
             GameNode(3, [], [2, 4, 5]),
             GameNode(4, [], [3, 5]),
             GameNode(5, [], [3, 4])]

    players = [RandomPlayer(0, [Unit(0, nodes[0])], [nodes[0]], nodes[0]),
               RandomPlayer(1, [Unit(1, nodes[1])], [nodes[1]], nodes[0]),
               RandomPlayer(2, [Unit(2, nodes[4])], [nodes[4]], nodes[0]),
               RandomPlayer(3, [Unit(3, nodes[5])], [nodes[5]], nodes[0])]

    nodes[0].add_unit(players[0].units[0])
    nodes[1].add_unit(players[1].units[0])
    nodes[4].add_unit(players[2].units[0])
    nodes[5].add_unit(players[3].units[0])
    
    graph = GameGraph(nodes)
    
    game = Game(players, graph)

    game.update_state([], False)
    
    ng = game.simulate()

    for r in range(100):
        # print "#######################################################"
        # print "                       Round %d" % r
        # print "#######################################################"

        # print "Simulated"
        # print ng.state

        # for m in sim_moves[0]:
        #     print m
                
        # print "Initial"
        # print game.state
        
        # for m in moves[0]:
        #     print m
        #
        s_moves = []
        g_moves = []
        
        for p in range(len(game.players)):
            moves = game.state.get_legal_moves(game.players[p])
            sim_moves = ng.state.get_legal_moves(ng.players[p])
            assert(len(sim_moves) == len(moves))
            for i in range(len(sim_moves)):
                assert(sim_moves[i] == moves[i])
            if len(moves) > 0:
                s_moves.append(sim_moves[0])
                g_moves.append(moves[0])
            
        ng.update_round(s_moves)
        game.update_round(g_moves)

            
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
    

def main(argv):
    test_sh_player()
    
    
if __name__ == "__main__":
    main(sys.argv[1:])
