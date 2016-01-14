import numpy as np
from gameGraph import EmptyNode
from matplotlib.colors import cnames
from itertools import product


class Unit(object):
    def __init__(self, player, node, action="nothing", target=EmptyNode()):
        self.player = player
        self.node = node
        self.action = action
        self.target = target
        self.color = cnames.values()[player]
        self.id = None
        
    def update(self):
        # Needed to make attackers stop attacking empty nodes after they have been conquered.
        if self.target.is_empty():
            if self.action == "attack":
                self.target.remove_attack()
            elif self.action == "support":
                self.target.remove_support()
                
            self.action = "nothing"
            
        if self.action == "nothing":
            self.target = EmptyNode()

    def __str__(self):
        return "Id: " + str(self.id) + "; Owner: " + str(self.player) + "; " + "Node: " + str(self.node.id) + ", "\
            "Performing: " + str(self.action) + " on " + str(self.target.id)
        
    def __eq__(self, other):
        if not self.id == other.id:
            return False
        if not self.player == other.player:
            return False
        if not self.node.id == other.node.id:
            return False
        if not self.action == other.action:
            return False
        if not self.target.id == other.target.id:
            return False
        return True

        
class EmptyUnit(Unit):
    def __init__(self):
        Unit.__init__(self, 100, EmptyNode(), "nothing", EmptyNode())
        self.id = "EMPTY"
        

class Player(object):
    def __init__(self, id, units, nodes, home):
        self.units = units
        self.nodes = nodes
        self.id = id
        self.home = home
        self.number = None
        self.color = None
        self.unit_cnt = 0
        for u in self.units:
            if u.id is None:
                u.id = str("p" + str(self.id) + "u" + str(self.unit_cnt))
            self.unit_cnt += 1

    def add_unit(self, unit):
        if unit.id is None:
            unit.id = str("p" + str(self.id) + "u" + str(self.unit_cnt))
        self.units.append(unit)
        self.unit_cnt += 1

    def remove_unit(self, unit):
        self.units.remove(unit)

    def update_home(self):
        if len(self.nodes) == 0:
            return  # Player has lost and will be removed from game
            
        if self.home not in self.nodes:
            self.home = self.nodes[0]
            
    def play(self, game):
        """
        :param game: A valid Game object, will be supplied by the GameEngine at runtime.
        :return: The list of  moves to be played by the player. One move per unit must be supplied.
        :rtype: a list(GameMove), with each move having unit, position origin, destination, action and target.

        This function **MUST BE IMPLEMENTED** for all player types constructed inheriting from this.
        
        This is the core function for all players that extend this game: the Game will supply
        functions to get all legal moves and simulate future states. It is advisable to use
        game.get_legal_moves(self) to obtain possible moves.
        """
        
        pass
        
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if self.id != other.id:
            return False
        if self.number != other.number:
            return False
        if not self.home == other.home:
            return False
        for i in range(len(self.units)):
            if not self[i] in other.units:
                return False
        for i in range(len(self.nodes)):
            if not self.nodes[i] in other.nodes:
                return False
                
        return True

    def __getitem__(self, index):
        return self.units[index]

    def __delitem__(self, index):
        del self.units[index]
        
    def __iter__(self):
        return self.units.__iter__()
        
    def __str__(self):
        st = "Player: " + str(self.id) + ", type: " + str(type(self)) + "\n"
        st += "Units:\n  *  " + "\n  *  ".join([str(u) for u in self.units]) + "\n"
        st += "Total units: " + str(len(self.units)) + "\n"
        st += "Nodes owned: " + ", ".join([str(n.id) for n in self.nodes]) + "\n"
        st += "Total nodes owned: " + str(len(self.nodes)) + "\n"
        return st

    def info(self):
        st = "Player: " + str(self.id) + ", type: " + str(type(self)) + "; "
        st += "Total units: " + str(len(self.units)) + "; "
        st += "Nodes owned: " + ", ".join([str(n.id) for n in self.nodes]) + "; "
        st += "Total nodes owned: " + str(len(self.nodes))
        return st


class RandomPlayer(Player):
    def __init__(self, *args):
        Player.__init__(self, *args)
    
    def play(self, game):
        chosen = []
        moves = game.state.get_legal_moves(self)
        for unit_moves in moves:
            chosen.append(unit_moves[np.random.choice(len(unit_moves), 1)])

        return chosen

        
class ShortHorizonPlayer(Player):
    def __init__(self, *args, **kwargs):
        Player.__init__(self, *args)
        self.unit_weight = kwargs.get("unit_weight", 1)
        self.node_weight = kwargs.get("node_weight", 3)
        self.occ_weight = kwargs.get("occ_weight", 2)
        self.occ_new_weight = kwargs.get("occ_new_weight", 1)
        self.n_enemies_weight = kwargs.get("n_enemies_weight", - 4)
        self.enemy_occ_nodes_weight = kwargs.get("enemy_occ_nodes_weight", - 1)
        self.enemy_unit_weight = kwargs.get("enemy_unit_weight", - 0.5)
        self.empty_node_weight = kwargs.get("empty_node_weight", 1)
        self.attacker_weight = kwargs.get("attacker_weight", -1)
        self.defender_weight = kwargs.get("defender_weight", 1)
        self.occ_attacker_weight = kwargs.get("occ_attacker_weight", - 1)
        self.occ_defender_weight = kwargs.get("occ_defender_weight", 1)
        self.enemy_occ_attacker_weight = kwargs.get("enemy_occ_attacker_weight", 0.5)
        self.enemy_occ_defender_weight = kwargs.get("enemy_occ_defender_weight", - 0.5)
        
        self.weights = []
        
    def gen_move_key(self, move_list):
        st = ""
        for m in move_list:
            st += ("O" + str(m.origin.id) + "D" + str(m.destination.id) + "A" +
                   str(m.action) + "T" + str(m.target.id))
        return ''.join(sorted(st))
            
    def play(self, game):
        chosen = []
        # Generate all possible combinations of single unit moves
        moves = [list(k) for k in product(*game.state.get_legal_moves(self))]
        max_utility = - 100000000000
        memo = {}
        round_weights = {}
        for i in range(len(moves)):
            # This is to not evaluate twice equivalent moves of the type:
            # same node, same action, different units.
            move_key = self.gen_move_key(moves[i])
            # We still want a chance of chosing this move randomly, if it's among the winning ones
            if move_key in memo:
                if memo[move_key] == max_utility:
                    chosen.append(moves[i])
                continue

            new_state = game.simulate()
            assert(new_state == game)
            # Replicate the same list but with copied objects
            n_moves = [list(k) for k in product(*new_state.state.get_legal_moves(new_state.players[self.id]))]
            move = n_moves[i]
            
            new_state.update_round([move])
            utility = self.evaluate_state(new_state.state)

            memo[move_key] = utility
            
            # This method of storing equivalent moves is just wrong. TODO: change.
            if utility > max_utility:
                chosen = [moves[i]]
                max_utility = utility
                round_weights[move_key] = self.get_weights(new_state.state)
            elif utility == max_utility:
                chosen.append(moves[i])
                round_weights[move_key] = self.get_weights(new_state.state)
                
            # Don't want memory usage to increase as game progresses
            del new_state
            
            # If there are multiple equivalent moves just pick one at random
        if len(chosen) > 0:
            c = np.random.choice(len(chosen), 1)
            chosen = chosen[c]
            self.weights.append(round_weights[self.gen_move_key(chosen)])
        
        return chosen
        
    def evaluate_state(self, state):
        u = 0
        future_self = state.players[self.id]
        # Do I have more units than now?
        u += (len(future_self.units) - len(self.units)) * self.unit_weight
        # Do I own more nodes than now?
        u += (len(future_self.nodes) - len(self.nodes)) * self.node_weight
        # Do I occupy more nodes than now?
        u += sum(self.occ_weight for n in state.graph if n.owner == future_self.id)
        # Do I occupy nodes that I don't now?
        u += sum(self.occ_new_weight for n in state.graph
                 if n.owner == future_self.id and n not in future_self.nodes)
        # How many enemies are there left
        u += (len(state.players) - 1) * self.n_enemies_weight
        # How many nodes do my enemies occupy
        u += sum(self.enemy_occ_nodes_weight for n in state.graph
                 if n.owner is not None and n.owner != future_self.id)
        # How many units do my enemies own
        u += sum(self.enemy_unit_weight for p in state.players.values() for u in p)
        # How many nodes are empty
        u += sum(self.empty_node_weight for n in state.graph if n.owner is None)
        # How many attackers are attacking my nodes
        u += sum(n.n_attacking * self.attacker_weight for n in future_self.nodes)
        # How many defenders are on my nodes
        u += sum(n.n_defending * self.defender_weight for n in future_self.nodes)
        # How many attackers on nodes occupied by me
        u += sum(n.n_attacking * self.occ_attacker_weight
                 for n in state.graph if n.owner == future_self.id)
        # How many defenders on nodes occupied by me
        u += sum(n.n_defending * self.occ_defender_weight
                 for n in state.graph if n.owner == future_self.id)
        # How many attackers on nodes occupied by enemies
        u += sum(n.n_attacking * self.enemy_occ_attacker_weight
                 for n in state.graph if n.owner is not None and n.owner != future_self.id)
        # how many defenders on nodes occupied by enemies
        u += sum(n.n_defending * self.enemy_occ_defender_weight
                 for n in state.graph if n.owner is not None and n.owner != future_self.id)

        return u

    def get_weights(self, state):
        future_self = state.players[self.id]
        w = {}
        w["unit_weight"] = len(future_self.units) - len(self.units)
        w["node_weight"] = len(future_self.nodes) - len(self.nodes)
        w["occ_weight"] = sum(1 for n in state.graph if n.owner == future_self.id)
        w["occ_new_weight"] = sum(1 for n in state.graph
                                  if n.owner == future_self.id and n not in future_self.nodes)
        w["n_enemies_weight"] = (len(state.players) - 1)
        w["enemy_occ_nodes_weight"] = sum(1 for n in state.graph
                                          if n.owner is not None and n.owner != future_self.id)
        w["enemy_unit_weight"] = sum(1 for p in state.players.values() for u in p)
        w["empty_node_weight"] = sum(1 for n in state.graph if n.owner is None)
        w["attacker_weight"] = sum(n.n_attacking for n in future_self.nodes)
        w["defender_weight"] = sum(n.n_defending for n in future_self.nodes)
        w["occ_attacker_weight"] = sum(n.n_attacking for n in state.graph if n.owner == future_self.id)
        w["occ_defender_weight"] = sum(n.n_defending for n in state.graph if n.owner == future_self.id)
        w["enemy_occ_attacker_weight"] = sum(n.n_attacking for n in state.graph
                                             if n.owner is not None and n.owner != future_self.id)
        w["enemy_occ_defender_weight"] = sum(n.n_defending for n in state.graph
                                             if n.owner is not None and n.owner != future_self.id)
        return w
