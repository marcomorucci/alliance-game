from Tkinter import *
import networkx as nx

master = Tk()


def adjust_coords(game_graph, cwidth=924, cheight=668, node_width=50, node_height=50):
    layout = nx.spring_layout(game_graph.graph)
    nl = {}

    for n in layout:
        if layout[n][0] == 0:
            x1 = (layout[n][0] + 0.05) * cwidth
        elif layout[n][0] == 1:
            x1 = (layout[n][0] - 0.05) * cwidth
        else:
            x1 = layout[n][0] * cwidth
            
        if layout[n][1] == 0:
            y1 = (layout[n][1] + 0.05) * cheight
        elif layout[n][0] == 1:
            y1 = (layout[n][1] - 0.05) * cheight
        else:
            y1 = layout[n][1] * cheight
            
        x2 = x1 + node_width
        
        y2 = y1 + node_height
            
        nl[n] = [x1, y1, x2, y2]
        
    return nl
        

def generate_units_layout(node_layout, n_units, unit_width, unit_height, node_width, node_height):
    layout = []
    incr_y = 0
    horiz_add = 0
    for i in range(n_units):
        horiz_add += 1
        
        x1 = node_layout[0] + node_width / 2 + (unit_width / 2 if i % 2 == 0 else (- unit_width))
        x2 = x1 + unit_width
        
        y1 = node_layout[1] + node_height / 5 + ((unit_height + 2) * incr_y)
        y2 = y1 + unit_height
        
        if horiz_add == 2:
            incr_y += 1
            horiz_add = 0
            
        layout.append([x1, y1, x2, y2])
    return layout
            
    
def draw_nodes(canvas, graph, layout, node_width, node_height):
    for k in layout:
        for e in range(len(graph[k].edges)):
            canvas.create_line([layout[k][0] + node_width / 2, layout[k][1] + node_height / 2,
                               layout[graph[k].edges[e]][0] + node_width / 2,
                               layout[graph[k].edges[e]][1] + node_height / 2])

    for i in layout:
         oid = canvas.create_oval(layout[i], fill=graph[i].color, tag="n" + str(graph[i].id))
    #     canvas.create_text(layout[i][2], layout[i][3], text=str(graph[i]))
 

def draw_units(canvas, graph, layout, node_width, node_height, unit_width, unit_height):

    for i in layout:
        ul = generate_units_layout(layout[i], len(graph[i]), unit_width,
                                   unit_height, node_width, node_height)
        for u in range(len(graph[i])):
            unit = graph[i][u]
            tag = str(i) + " " + str(u)
            u_pos = ul[u]
            uid = canvas.create_oval(ul[u], fill=unit.color, activefill="red", tags=tag)
            if graph[i][u].action == "attack":
                canvas.create_line([ul[u][0] + unit_width / 2, ul[u][1] + unit_height / 2,
                                   (layout[unit.target.id][0] + node_width / 2) / 2,
                                   (layout[unit.target.id][1] + node_height / 2) / 2,
                                   layout[unit.target.id][0] + node_width / 2,
                                   layout[unit.target.id][1] + node_height / 2],
                                   fill="red", smooth=True)
            elif unit.action == "support":
                canvas.create_line([ul[u][0] + unit_width / 2, ul[u][1] + unit_height / 2,
                                    (layout[unit.target.id][0] + node_width / 2) / 2,
                                    (layout[unit.target.id][1] + node_height / 2) / 2,
                                    layout[unit.target.id][0] + node_width / 2,
                                    layout[unit.target.id][1] + node_height / 2],
                                   fill="blue", smooth=True)
            
            unit.draw_pos = canvas.coords(uid)

            # This is needed because tkinter works in mysterious ways.
            def make_lambda(unit, uid, canvas, graph):
                return lambda ev: unit.on_click(ev, uid, canvas, graph)
                
            canvas.tag_bind(uid, "<ButtonPress-1>", make_lambda(unit, uid, canvas, graph))
            

def draw_player_info(master, players):
    for p in players:
        w = Label(master, text=str(p))
        w.pack(side=LEFT)


def draw(f, w, layout, game, **kwargs):
    node_width = kwargs.get("node_width", 50)
    node_height = kwargs.get("node_height", 50)
    unit_width = kwargs.get("unit_width", 10)
    unit_height = kwargs.get("unit_height", 10)
    
    w.delete("all")
    draw_nodes(w, game.graph, layout, node_width, node_height)
    draw_units(w, game.graph, layout, node_width, node_height, unit_width, unit_height)
    for w in f.winfo_children():
        w.destroy()
    draw_player_info(f, game.players.values())


def draw_winner(w, win):
    l = Label(w, text="Player %d wins" % win)
    l.pack()

    
def setup(game, round_step_fcn, **kwargs):
    canvas_width = kwargs.get("canvas_width", 1024)
    canvas_height = kwargs.get("canvas_height", 768)
    canvas_margin_x = kwargs.get("canvas_margin_x", 100)
    canvas_margin_y = kwargs.get("canvas_margin_y", 100)
    node_width = kwargs.get("node_width", 50)
    node_height = kwargs.get("node_height", 50)
    info_box_width = kwargs.get("info_box_width", 50)
    info_box_height = kwargs.get("info_box_height", 50)

    frame = Frame(master, width=canvas_width + info_box_width + 10, height=canvas_height + info_box_height + 10)
            
    frame.bind("<Key>", round_step_fcn)

    w = Canvas(frame, width=canvas_width, height=canvas_height)
    w.pack()

    f = Frame(frame, width=info_box_width, height=info_box_height)
    f.pack()

    frame.pack()
    frame.focus_set()
    layout = adjust_coords(game.graph, canvas_width - canvas_margin_x,
                           canvas_height - canvas_margin_y, node_width, node_height)

    return f, w, layout

    
def show():
    mainloop()
