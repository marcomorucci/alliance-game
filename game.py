#!/usr/bin/env python
from player import Unit, EmptyUnit
from gameGraph import EmptyNode, GameNode, GameGraph
from copy import deepcopy
import numpy as np
from matplotlib.colors import cnames


class GameMove(object):
    def __init__(self, unit=None, origin=None, destination=None, action=None, target=None):
        self.origin = origin
        self.destination = destination
        self.action = action
        self.target = target
        self.unit = unit

    def __eq__(self, other):
        return self.origin.id == other.origin.id and \
            self.destination.id == other.destination.id and \
            self.action == other.action and self.target.id == other.target.id
        
    def __str__(self):
        return "origin: node " + str(self.origin.id) + \
            "; destination: node " + str(self.destination.id) + \
            "; action: " + self.action + "; target: node " + str(self.target.id)


class GameState(object):
    def __init__(self, gameGraph, players):
        self.players = players
        self.graph = gameGraph
        
    def __eq__(self, other):
        for p in self.players:
            if p not in other.players:
                return False
            if not self.players[p] == other.players[p]:
                return False
                
        if not self.graph == other.graph:
            return False

        return True
        
    def update(self, moves, DEBUG=False):
        for m in moves:
            self.add_move(m, DEBUG)
                        
        self.update_nodes()
    
    def add_move(self, move, DEBUG=False):
        if DEBUG:
            print "####################################################################################"
            print "Evaluating Move", move
            print "Origin node BEFORE move", move.origin
        # These two methods must be called in this order. This makes sure actions are updated
        # only after movement has occurred.
        moved = self.update_positions(move)
        if moved:
            if DEBUG:
                print "Movement successful"
            self.update_actions(move)
        else:
            if DEBUG:
                print "Movement not successful"
            # If the unit tried to move to an occupied block, move it back to its origin.
            self.update_actions(GameMove(move.unit, move.origin, move.origin,
                                         "nothing", EmptyNode()))
            
        if DEBUG:
            print "Unit after move", move.unit
            print "Destination Node after move", move.destination
            print "Target after move", move.target
            print "Origin Node after move", move.origin

    def update_positions(self, move):
        # Given that states are updated once all moves have been made and that players
        # don't know what others are doing until the state has been updated
        # it is possible that two players choose to move on an empty node.
        # In this case, I have chosen to give the node to the first mover.
        if move.destination.owner == move.unit.player or move.destination.is_empty():
            move.origin.remove_unit(move.unit)
            move.destination.add_unit(move.unit)
            move.unit.node = move.destination
            # This is to confirm the success of the move. Needed to update action.
            return True
        else:
            return False
    
    def update_actions(self, move):
        move.unit.action = move.action
        move.unit.target = move.target
        
    def update_nodes(self):
        for node in self.graph.nodes.values():  # TODO: Replace with list getter
            if node.n_attacking > node.n_defending:
                # Make each unit back off by creating a fake move
                for u in node.units:
                    pos = [p for p in self.get_legal_positions(u) if not p == u.node]
                    if len(pos) > 0:
                        move = GameMove(unit=u, origin=node,
                                        destination=pos[np.random.choice(len(pos), 1)],
                                        action="nothing", target=EmptyNode())
                        self.update_positions(move)
                        self.update_actions(move)
                    else:
                        self.destroy_unit(u)
                                      
            # There can only be units owned by 1 player at any time on a node.
            # It makes sense that all the units in the array will have the same
            # owner, given how movement is regulated. So it doesn't' matter which one we pick.
            if len(node.units) > 0:
                node.change_ownership(node.units[0].player)
            else:
                node.change_ownership(None)

            node.n_attacking = 0
            node.n_defending = len(node.units)
            
        for n in self.graph:
            for u in n:
                if u.target.is_empty():
                    u.action = "nothing"
                if u.action == "attack":
                    u.target.add_attack()
                elif u.action == "support":
                    u.target.add_support()
                else:
                    u.target = EmptyNode()
                    
    def build_units(self, DEBUG):
        if DEBUG:
            print "                            BUILDING PHASE"
        for p in self.players.values():
            if DEBUG:
                print "Player", p.id
            if len(p.units) < len(p.nodes):
                # For as many nodes as the difference, add units to the player home.
                n_units = len(p.nodes) - len(p.units)
                if DEBUG:
                    print "Building %d units" % n_units
                for i in range(n_units):
                    u = Unit(p.id, p.home, "nothing", EmptyNode())
                    p.add_unit(u)
                    p.home.add_unit(u)
                    if DEBUG:
                        print "Unit added to node:", p.home
                    
    def destroy_unit(self, unit):
        self.players[unit.player].remove_unit(unit)
        unit.node.remove_unit(unit)
        unit = EmptyUnit()
        
    def update_ownership(self, DEBUG=False):
        if DEBUG:
            print "                           UPDATING NODE OWNERSHIP"
        for p in self.players.values():
            for n in p.nodes:
                if len(n.units) > 0 and n.owner != p.id:
                    if DEBUG:
                        print "Node %d removed from player %d" % (n.id, p.id)
                    p.nodes.remove(n)
                    n.color = cnames["white"]
    
        for p in self.players.values():
            for u in p:
                # TODO: should be switched to a set union (make nodes hashable by # first)
                if u.node not in p.nodes:
                    if DEBUG:
                        print "Node %d added to player %d" % (u.node.id, p.id)
                    p.nodes.append(u.node)
                    u.node.color = cnames.values()[u.player]
            p.update_home()
            
    def get_legal_positions(self, unit):
        positions = []
        for n in unit.node.edges:
            next_node = self.graph.get_node(n)
            if next_node.is_empty() or next_node.owner == unit.player:
                positions.append(next_node)
        positions.append(unit.node)
        return positions
                
    def get_legal_actions(self, pos, unit):
        actions = []
        for e in pos.edges:
            node = self.graph.get_node(e)
            if not node.is_empty() and node.owner != unit.player:
                actions.append({"action": "support", "target": node})
                actions.append({"action": "attack", "target": node})
        actions.append({"action": "nothing", "target": EmptyNode()})
        return actions
        
    def get_legal_moves(self, player):
        moves = []
        for u in player:
            positions = self.get_legal_positions(u)
            unit_moves = []
            for p in positions:
                for a in self.get_legal_actions(p, u):
                    unit_moves.append(GameMove(unit=u,
                                               origin=u.node,
                                               destination=p,
                                               action=a["action"],
                                               target=a["target"]))
            moves.append(unit_moves)
        return moves

    def __str__(self):
        return "Players:" + "".join([p.__str__() for p in self.players.values()]) + "\n" + \
            str(self.graph) + "\n***********************\n"


class Game(object):
    def __init__(self, players, graph, fall=False):
        self.players = {p.id: p for p in players}
        self.state = GameState(graph, self.players)
        self.fall = fall
        self.round_n = 1
        
        # Assign player numbers
        i = 0
        for p in self.players.values():
            if p.number is None:
                p.number = i
                i += 1

    def __eq__(self, other):
        if self.fall != other.fall:
            return False

        # Players are getting checked here
        if not self.state == other.state:
            return False
            
        return True
        
    def get_current_state(self):
        return self.state

    def update_state(self, moves, DEBUG=False):
        self.state.update(moves, DEBUG)

    # TODO: This needs to be refactored into class-specific deepcopy methods
    def simulate(self):
        nodes = {}
        for n in self.state.graph:
            nodes[n.id] = GameNode(id=n.id, edges=n.edges, owner=n.owner, units=[])
            nodes[n.id].n_attacking = n.n_attacking
            nodes[n.id].n_defending = n.n_defending
            nodes["EMPTY"] = EmptyNode()
            
        players = {}
        for p in self.players.values():
            p_nodes = [nodes[n.id] for n in p.nodes]
            np = p.__class__(p.id, [], p_nodes, nodes[p.home.id])
            np.number = p.number
            players[np.id] = np
            
        for n in self.state.graph:
            for u in n:
                nu = Unit(u.player, nodes[n.id], u.action, nodes[u.target.id])
                nu.id = u.id
                nodes[n.id].units.append(nu)
                players[u.player].add_unit(nu)

        nodes.pop("EMPTY", None)
        return Game([players[p] for p in self.players],
                    GameGraph([nodes[n.id] for n in self.state.graph]), self.fall)

    def play_round(self, DEBUG=False):
        if DEBUG:
            print "********************************************************************************************"
            print "                                       Round %d" % self.round_n
            print "********************************************************************************************"

        for p in self.players.values():
            moves = [p.play(self)]
            w = self.update_round(moves, DEBUG)
            if w is not None:
                return w

        self.fall = not self.fall
        self.round_n += 1
        
        self.players = {self.players[p].id: self.players[p] for p in self.players if len(self.players[p].nodes) > 0}
        self.state.players = self.players
        
        return None
    
    def update_round(self, moves, DEBUG=False):
        
        if len(self.players) == 1:
            return self.players.keys()[0]

        if DEBUG:
            print "                        EVALUATING MOVES"

        for m in moves:
            if DEBUG:
                print "-------------------------- Player %d -------------------------" % m[0].unit.player
            self.update_state(m, DEBUG=DEBUG)

        if self.fall:
            if DEBUG:
                print "                        FALL ROUND: %s" % str(self.fall)
            self.state.update_ownership(DEBUG)
            self.state.build_units(DEBUG)

        if DEBUG:
            print "+++++++++++++++++++++++++++++++++ END OF ROUND STATE +++++++++++++++++++++++++++++++"
            print self.state
        return None
