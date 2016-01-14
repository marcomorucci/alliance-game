import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import cnames
import inspect


class GameNode(object):
    def __init__(self, id, units, edges, owner=None):
        self.units = units
        self.edges = edges
        self.id = id
        self.n_defending = len(units)
        self.n_attacking = 0
        self.owner = owner
        self.color = cnames["white"]
        
    def get_edge_pairs(self):
        return [(self.id, edge) for edge in self.edges]

    def add_unit(self, unit):
        self.units.append(unit)
        self.add_support()
        
    def remove_unit(self, unit):
        if unit not in self.units:
            print "Node", self.id
            print inspect.stack()[1][3]
            print "To Remove:", unit
            print "Others",
            for u in self.units:
                print u,
            print ""
        self.units.remove(unit)
        self.remove_support()
        
    def add_support(self):
        self.n_defending += 1
        
    def add_attack(self):
        self.n_attacking += 1

    def remove_support(self):
        self.n_defending -= 1
        
    def remove_attack(self):
        self.n_attacking -= 1
        
    def change_ownership(self, new_owner):
        self.owner = new_owner

    def is_empty(self):
        return len(self.units) == 0
        
    def is_null(self):
        return False
        
    def __getitem__(self, key):
        return self.units[key]
        
    def __iter__(self):
        return self.units.__iter__()
        
    def __len__(self):
        return len(self.units)
        
    def __str__(self):
        st = "Node: " + str(self.id) + "\n"
        st += "Neighbours: " + ", ".join([str(e) for e in self.edges]) + "\n"
        st += "Total attacking: " + str(self.n_attacking) + "; total defending: " + str(self.n_defending) + "\n"
        st += "Owner: player " + str(self.owner) + "\n"
        st += "Units:\n  *  " + "\n  *  ".join([str(u) for u in self.units])
        return st

    def __eq__(self, other):
        if self.id != other.id:
            return False
        if self.edges != other.edges:
            return False
        if self.n_attacking != other.n_attacking:
            return False
        if self.n_defending != other.n_defending:
            return False
        if self.owner != other.owner:
            return False
            
        for i in range(len(self)):
            if len(self.units) != len(other.units):
                return False
            if not self[i] in other.units:
                return False
                
        return True

            
class EmptyNode(GameNode):
    def __init__(self):
        GameNode.__init__(self, "EMPTY", [], [], None)
        
    def is_null(self):
        return True
        
    def __str__(self):
        return "Empty Node"
        
    
class GameGraph(object):
    def __init__(self, nodes):
        self.nodes = {n.id: n for n in nodes}
        self.graph = nx.Graph()
        self.graph.add_nodes_from([n.id for n in self.nodes.values()])
        edges = []
        for n in self.nodes.values():
            edges += n.get_edge_pairs()
        self.graph.add_edges_from(edges)
        self.graph = self.graph.to_undirected()

    def get_node(self, node_id):
        return self.nodes[node_id]
                
    def draw(self, show=True):
        node_colors = [(n.owner if n.owner is not None else 5) for n in self.nodes.values()]
        nx.draw_networkx(self.graph, cmap=plt.get_cmap("Paired"), node_color=node_colors)

        if show:
            plt.show()

    def __getitem__(self, key):
        return self.nodes[key]
        
    def __iter__(self):
        return self.nodes.values().__iter__()
            
    def __str__(self):
        return "Game Graph:\n" + "\n".join([str(n) for n in self.nodes.values()])

    def __eq__(self, other):
        for n in self.nodes:
            if n not in other.nodes:
                return False
            if not self[n] == other[n]:
                return False
        
        return True

        
if __name__ == "__main__":
    nodes = [GameNode(0, "NA", [1, 2]),
             GameNode(1, "NA", [0, 2]),
             GameNode(2, "NA", [0, 1, 3]),
             GameNode(3, "NA", [2, 4, 5]),
             GameNode(4, "NA", [3, 5]),
             GameNode(5, "NA", [3, 4])]
    g = GameGraph(nodes)
    g.draw()
