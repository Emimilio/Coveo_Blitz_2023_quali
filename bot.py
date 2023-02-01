from game_message import Tick, Action, Spawn, Sail, Dock, Anchor, directions


class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")
        self.map_topo = None
        self.moves = []
        self.wanted_port = []
        self.bad_port = {}
        self.tide_schedule = []
        self.temporary_ban = None
        self.port_num = 0
        self.start_port = ()
        self.first_quarter = {}
        self.second_quarter = {}
        self.third_quarter = {}
        self.fourth_quarter = {}
        self.all_port = []
        self.port_index = {}
        self.port_sequence = []
        self.boat_posi = ()
        self.the_port = None

    def var_setup(self, tick: Tick):
        self.port_num = len(tick.map.ports)
        for index, port in enumerate(tick.map.ports):
            port_posi = (port.row, port.column)
            self.all_port.append(port_posi)
            self.bad_port[port_posi] = 0
            self.port_index[port_posi] = index

    def best_spawn(self, tick: Tick):
        best = 100000
        start_posi = (29, 14)
        best_port = None
        for index, port in enumerate(tick.map.ports):
            port_posi = (port.row, port.column)
            if self.heuristic(start_posi, port_posi) < best:
                best = self.heuristic(start_posi, port_posi)
                best_port = port

            '''if port_posi[0] < 30 and port_posi[1] < 30:
                self.first_quarter[port_posi] = index
            elif port_posi[0] < 30 and port_posi[1] >= 30:
                self.second_quarter[port_posi] = index
            elif port_posi[0] >= 30 and port_posi[1] >= 30:
                self.third_quarter[port_posi] = index
            elif port_posi[0] >= 30 and port_posi[1] < 30:
                self.fourth_quarter[port_posi] = index'''

        return best_port

    def heuristic(self, start, finish):
        return (((finish[0] - start[0])**2 + (finish[1] - start[1])**2)**0.5)*10

    def gValue(self, start, finish):
        row_variation = abs(finish[0] - start[0])
        column_variation = abs(finish[1] - start[1])

        return (max(row_variation, column_variation))*10

    def quarter_ports(self, tick: Tick, quarter):
        boat_posi = (tick.currentLocation.row, tick.currentLocation.column)
        best = 10000
        best_port = None
        for port, index in quarter.items():
            if index in tick.visitedPortIndices:
                continue
            if (self.bad_port[port] >= 6) and (port != self.start_port):
                continue
            if port == self.temporary_ban:
                continue
            if self.heuristic(boat_posi, port) < best:
                best = self.heuristic(boat_posi, port)
                best_port = port
        return best_port

    def bestPort(self, tick: Tick):
        if self.quarter_ports(tick, self.first_quarter) is not None:
            return self.quarter_ports(tick, self.first_quarter)
        if self.quarter_ports(tick, self.second_quarter) is not None:
            return self.quarter_ports(tick, self.second_quarter)
        if self.quarter_ports(tick, self.third_quarter) is not None:
            return self.quarter_ports(tick, self.third_quarter)
        if self.quarter_ports(tick, self.fourth_quarter) is not None:
            return self.quarter_ports(tick, self.fourth_quarter)
        return self.start_port


    def neiborNodes(self, node_posi):
        #neibors = []
        dico = {}

        if node_posi[0] > 0:
            #neibors.append((node_posi[0] - 1, node_posi[1]))
            dico[(node_posi[0] - 1, node_posi[1])] = 10

        if node_posi[0] < 59:
            #neibors.append((node_posi[0] + 1, node_posi[1]))
            dico[(node_posi[0] + 1, node_posi[1])] = 10

        if node_posi[1] > 0:
            #neibors.append((node_posi[0], node_posi[1] - 1))
            dico[(node_posi[0], node_posi[1] - 1)] = 10

        if node_posi[1] < 59:
            #neibors.append((node_posi[0], node_posi[1] + 1))
            dico[(node_posi[0], node_posi[1] + 1)] = 10

        if node_posi[0] > 0 and node_posi[1] < 59: #top right
            #neibors.append((node_posi[0] - 1, node_posi[1] + 1))
            dico[(node_posi[0] - 1, node_posi[1] + 1)] = 14

        if node_posi[0] > 0 and node_posi[1] > 0: #top left
            #neibors.append((node_posi[0] - 1, node_posi[1] - 1))
            dico[(node_posi[0] - 1, node_posi[1] - 1)] = 14

        if node_posi[0] < 59 and node_posi[1] > 0: #botom left
            #neibors.append((node_posi[0] + 1, node_posi[1] - 1))
            dico[(node_posi[0] + 1, node_posi[1] - 1)] = 14

        if node_posi[0] < 59 and node_posi[1] < 59: #botom right
            #neibors.append((node_posi[0] + 1, node_posi[1] + 1))
            dico[(node_posi[0] + 1, node_posi[1] + 1)] = 14
        
        #return neibors
        return dico

    def sortDict(self, dico):
        return dict(sorted(dico.items(), key=lambda item: item[1]))

    def pathFinder(self, parent, port):
        best_path = []
        wanted_item = port

        while(wanted_item in parent.keys()):
            best_path.insert(0, wanted_item)
            wanted_item = parent.get(wanted_item)
        best_path.insert(0, wanted_item)
        
        return best_path
    
    def A_star(self, tick: Tick, port):

        boat_posi = (tick.currentLocation.row, tick.currentLocation.column)
        visited_node = []
        openSet = {boat_posi: self.heuristic(boat_posi, port)}
        parent = {}
        top_Gvalue = {boat_posi: 0}
        while len(openSet) > 0:
            best_cost = 10000
            current_node = boat_posi
            for node, fcost in openSet.items():
                if fcost < best_cost:
                    best_cost = fcost
                    current_node = node
                elif fcost == best_cost and (self.heuristic(node, port) < self.heuristic(current_node, port)):
                    current_node = node

            if current_node == port:
                path = self.pathFinder(parent, port)
                print(f"this is the best fucking path {path} ***********************************************")
                return path

            openSet.pop(current_node)
            visited_node.append(current_node)

            for neibor, variation in self.neiborNodes(current_node).items():
                if neibor in visited_node:
                    continue

                if self.map_topo[neibor[0]][neibor[1]] >= self.tide_schedule[(self.gValue(boat_posi, neibor) // 10) % 10]:
                    continue

                if neibor not in top_Gvalue.keys():
                    top_Gvalue[neibor] = top_Gvalue[current_node] + variation
                    parent[neibor] = current_node
                    openSet[neibor] = self.heuristic(neibor, port) + top_Gvalue[neibor]
                elif top_Gvalue[neibor] > (top_Gvalue[current_node] + variation):
                    top_Gvalue[neibor] = top_Gvalue[current_node] + variation
                    parent[neibor] = current_node
                    openSet[neibor] = self.heuristic(neibor, port) + top_Gvalue[neibor]
        
        print("no path available")

        return None

    def coortranslator(self, path):
        moves = []

        for index, posi in enumerate(path):
            if index == len(path) - 1:
                break
            next_posi = path[index + 1]
            variation = (next_posi[0] - posi[0], next_posi[1] - posi[1])

            if variation == (0, 1):
                moves.append("E")
            elif variation == (1, 0):
                moves.append("S")
            elif variation == (0, -1):
                moves.append("W")
            elif variation == (-1, 0):
                moves.append("N")
            elif variation == (1, 1):
                moves.append("SE")
            elif variation == (-1, -1):
                moves.append("NW")
            elif variation == (-1, 1):
                moves.append("NE")
            elif variation == (1, -1):
                moves.append("SW")
            else:
                print("somthing is wrong I cant find a move to do")
        moves.append(Dock())

        return moves

    def four_closest_port(self, tick: Tick):
        boat_posi = self.boat_posi
        four_best_ports = []
        banned_port = []
        depth = self.depth_lvl(tick)
        if depth == 0:
            return [self.start_port]

        while len(four_best_ports) != depth:
            best_port = self.start_port
            best = 100000
            for index, port in enumerate(tick.map.ports):
                if (port.row, port.column) == self.start_port:
                    continue
                if index in tick.visitedPortIndices:
                    continue
                if (self.bad_port[(port.row, port.column)] >= 6) and ((port.row, port.column) != self.start_port):
                    continue
                if (port.row, port.column) in banned_port:
                    continue
                if self.heuristic(boat_posi, (port.row, port.column)) < best:
                    best = self.heuristic(boat_posi, (port.row, port.column))
                    best_port = (port.row, port.column)
            four_best_ports.append(best_port)
            banned_port.append(best_port)
        return four_best_ports

    def depth_lvl(self, tick: Tick):
        depth = 6
        if len(tick.visitedPortIndices) > self.port_num - 6:
            depth = self.port_num - len(tick.visitedPortIndices)
        return depth

    def best_fucking_path(self, tick: Tick, best_ports):
        if self.depth_lvl(tick) == 0:
            return [self.start_port]
        openset = {((tick.currentLocation.row, tick.currentLocation.column),): 0}
        valid_path = {}
        best = 1000000
        best_path = []
        while len(openset) > 0:
            my_list = list(openset.keys())
            curent_path = my_list[0]
            distance = openset[curent_path]
            if (len(curent_path) - 1) == len(best_ports):
                valid_path[curent_path] = distance
                openset.pop(curent_path)
                continue

            openset.pop(curent_path)
            for port in best_ports:
                if port in curent_path:
                    continue
                new_path = curent_path + (port,)
                openset[new_path] = distance + self.heuristic(curent_path[-1], port)

        for path, dist in valid_path.items():
            if dist < best:
                best = dist
                best_path = path[1::]
        return best_path

    def get_next_move(self, tick: Tick) -> Action:

        self.map_topo = tick.map.topology
        if tick.currentLocation is None:
            self.var_setup(tick)
            spawn = self.best_spawn(tick)
            self.start_port = (spawn.row, spawn.column)
            self.the_port = self.start_port
            return Spawn(spawn)
        if tick.currentTick == 1:
            return Dock()

        self.boat_posi = (tick.currentLocation.row, tick.currentLocation.column)
        self.tide_schedule = tick.tideSchedule

        close_ports = self.four_closest_port(tick)
        print(f"THIS IS THE SPAWNING PORT {self.start_port}")
        print(f"THESE ARE THE CLOSEST PORTS{close_ports}")
        print(f"THIS IS THE BEST PORTS {self.port_sequence}")
        if self.port_index[self.the_port] in tick.visitedPortIndices or ((self.bad_port[self.the_port] >= 6) and (self.the_port != self.start_port)):
            self.port_sequence = self.best_fucking_path(tick, close_ports)
            print(f"THIS IS THE BEST PORTS {self.port_sequence}")
            if len(self.port_sequence) == 0:
                self.the_port = self.start_port
            else:
                self.the_port = self.port_sequence[0]

        path = self.A_star(tick, self.the_port)
        if path is None:
            if self.bad_port[self.the_port] < 6:
                self.bad_port[self.the_port] += 1
                return Anchor()
            else:
                return Anchor()
        else:
            self.moves = self.coortranslator(path)

        move = self.moves[0]
        if type(move) == str:
            return Sail(move)
        else:
            return move
