import pygame as pg
from os import path
import heapq
vec = pg.math.Vector2
import math



DARKGRAY = (40, 40, 40)
MEDGRAY = (75, 75, 75)
LIGHTGRAY = (140, 140, 140)
SAFETYPADDINGCOLOR = (204, 162, 10)
GREEN = (60,179,113)

screen = pg.display.set_mode((1280, 640))

class Environment:
    def __init__(self, pixelWidth, pixelHeight, agvPixelSize, obstacles, listOfAGVs):
        self.pixelWidth = pixelWidth 
        self.pixelHeight = pixelHeight 
        self.agvPixelSize = agvPixelSize
        self.screen = pg.display.set_mode((pixelWidth, pixelHeight))
        self.tileWidth = pixelWidth / agvPixelSize
        self.tileHeight = pixelHeight / agvPixelSize
        self.obstacles = []
        self.connections = [vec(1, 0), vec(-1, 0), vec(0, 1), vec(0, -1), vec(1, 1), vec(-1, 1), vec(1, -1), vec(-1, -1)] #possible movements:  right, left, up and down
        self.safetyPaddingAll = []  
        self.safetyPaddingCorners = [] 
        self.safetyPaddingNOCorners = [] 
        self.listOfAGVs = []

    def in_bounds(self, node): 
        return 0 <= node.x < self.pixelWidth and 0 <= node.y < self.pixelHeight

    def passable(self, node):
        return node not in self.obstacles

    def find_neighbors(self, node):
        neighbors = [node + connection for connection in self.connections]
        neighbors = filter(self.in_bounds, neighbors)
        neighbors = filter(self.passable, neighbors)
        return neighbors

    def calculate_safety_padding(self):
        #find all safety padding nodes/tiles
        for node in obstacles:
            for connection in self.connections:
                if (node + connection) not in obstacles and (node + connection) not in self.safetyPaddingAll:
                    self.safetyPaddingAll.append(vec2int(node + connection))
 
        #find corner padding nodes/tiles
        for node in obstacles:
            if (node + vec(0, 1)) not in obstacles and (node + vec(-1, 0)) not in obstacles: # down and left
                corner = (node + vec(-1, 1))
                self.safetyPaddingCorners.append(corner)
            if (node + vec(-1, 0)) not in obstacles and (node + vec(0, -1))not in obstacles:# left and up
                corner = (node + vec(-1, -1))
                self.safetyPaddingCorners.append(corner)
            if (node + vec(0, -1)) not in obstacles and (node + vec(1, 0))not in obstacles: # up and right
                corner = (node + vec(1, -1))
                self.safetyPaddingCorners.append(corner)
            if (node + vec(1, 0)) not in obstacles and (node + vec(0, 1))not in obstacles: # right and down
                corner = (node + vec(1, 1))
                self.safetyPaddingCorners.append(corner)

            for j in range(len(self.safetyPaddingCorners)):
                self.safetyPaddingCorners[j] = vec2int(vec(self.safetyPaddingCorners[j]))

        #remove corner padding nodes from all padding nodes
        self.safetyPaddingNOCorners = [k for k in self.safetyPaddingAll if k not in self.safetyPaddingCorners]
        return self.safetyPaddingCorners, self.safetyPaddingNOCorners

class PriorityQueue:
    #heapq binary tree
    def __init__(self):
        self.nodes = []

    def put(self, node, cost):
        heapq.heappush(self.nodes, (cost, node))

    def get(self):
        return heapq.heappop(self.nodes)[1]

    def empty(self):
        return len(self.nodes) == 0  #if = 0, return True

class PathPlanning:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def get_path(self, start, end):
        self.start = start
        self.end = end

class Astar(PathPlanning):
    #calculate path:
    def __init__(self, start, end, safetyPaddingCorners, safetyPaddingNOCorners):
        super().__init__(start, end)
        self.weights = {}
        self.start = start
        self.end = end
        self.safetyPaddingCorners = safetyPaddingCorners
        self.safetyPaddingNOCorners = safetyPaddingNOCorners

    def cost(self, from_node, to_node):
        if (vec(to_node) - vec(from_node)).length_squared() == 1:#if distance is 1, we're moving vertically or horizontally
            return self.weights.get(to_node, 0) + 10   #return 0 if it's no in the weights list -- if there' no weigh assigned to it, the default weight will be 0
        else:
            return self.weights.get(to_node, 0) + 14

    #add costs to padding nodes/tiles:
    def safety_padding_costs(self, safetyPaddingNOCorners):
        self.safetyPaddingNOCorners = safetyPaddingNOCorners
        for tile in self.safetyPaddingNOCorners:
            self.weights[tile] = 16

    def safety_padding_costs2(self, safetyPaddingCorners):
        self.safetyPaddingCorners = safetyPaddingCorners
        for tile in self.safetyPaddingCorners:
            self.weights.update({tile: 9})  

    def heuristic(self, node1, node2):
        # Euclidian distance calculation:
        return (math.sqrt(abs(node1.x - node2.x)** 2 + abs(node1.y - node2.y)** 2)) * 10

    def a_star_search(self, graph): 
        frontier = PriorityQueue()
        frontier.put(vec2int(self.start), 0)
        path = {}
        costl = {}
        path[vec2int(self.start)] = None
        costl[vec2int(self.start)] = 0

        while not frontier.empty():
            current = frontier.get()
            if current == self.end:
                break
            for nextTile in graph.find_neighbors(vec(current)):
                nextTile = vec2int(nextTile)
                next_cost = costl[current] + self.cost(current, nextTile)
                if nextTile not in costl or next_cost < costl[nextTile]:
                    costl[nextTile] = next_cost
                    priority = next_cost + self.heuristic(self.end, vec(nextTile))
                    frontier.put(nextTile, priority)
                    path[nextTile] = vec(current) - vec(nextTile)
        return path, costl

class AGV(pg.sprite.Sprite):

    def __init__(self, agvPixelSize, environment, path_planning: PathPlanning = None):
        pg.sprite.Sprite.__init__(self)
        self.tasks = []
        self.agvPixelSize = agvPixelSize
        self.path_planning: PathPlanning = path_planning
        self.environment = environment
        self.speedx = 0
        self.speedy = 0

def draw_path_arrows(path, start, goal, agvPixelSize):
    #draw path with arrows:
    arrows = {}
    arrow_img = pg.image.load('arrowRight.png').convert_alpha()
    
    arrow_img = pg.transform.scale(arrow_img, (12, 12))
    for direction in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
        arrows[direction] = pg.transform.rotate(arrow_img, vec(direction).angle_to(vec(1, 0)))
    current = start 
    l = 0
    while current != goal:
        v = path[(current.x, current.y)]
        if v.length_squared() == 1:        
            l += 10
        else:
            l += 14
        img = arrows[vec2int(v)]
        x = current.x * agvPixelSize + agvPixelSize / 2
        y = current.y * agvPixelSize + agvPixelSize / 2
        r = img.get_rect(center=(x, y))
        screen.blit(img, r)
        current = current + path[vec2int(current)]

def draw(obstacles, weights, agvPixelSize):
    #draw obstacles:
    for obstacle in obstacles:
        rect = pg.Rect(obstacle * agvPixelSize, (agvPixelSize, agvPixelSize))
        pg.draw.rect(screen, LIGHTGRAY, rect)

    #draw safety padding:
    for tile in weights:
        x, y = tile
        rect = pg.Rect(x * agvPixelSize + 3, y * agvPixelSize + 3, agvPixelSize - 5, agvPixelSize - 5)
        pg.draw.rect(screen, SAFETYPADDINGCOLOR, rect)

    #draw tiles in drawing tool:
    for tile in getTileCoordinate:
        rect = pg.Rect(tile * agvPixelSize, (agvPixelSize, agvPixelSize))
        pg.draw.rect(screen, GREEN, rect)

def draw_icons(environment, start, goal, agvPixelSize):
    pixelWidth = environment.pixelWidth
    pixelHeight = environment.pixelHeight
    agvPixelSize = agvPixelSize

    start_img = pg.image.load('start.png').convert_alpha()
    start_img = pg.transform.scale(start_img, (25, 25))
    start_img.fill((0, 255, 0, 255), special_flags=pg.BLEND_RGBA_MULT)
    workstation_img = pg.image.load('workstation.png').convert_alpha()
    workstation_img = pg.transform.scale(workstation_img, (25, 25))
    workstation_img.fill((255, 0, 0, 255), special_flags=pg.BLEND_RGBA_MULT)

    start_center = (start.x * agvPixelSize + agvPixelSize / 2, start.y * agvPixelSize + agvPixelSize / 2)
    screen.blit(start_img, start_img.get_rect(center=start_center))
    goal_center = (goal.x * agvPixelSize + agvPixelSize / 2, goal.y * agvPixelSize + agvPixelSize / 2)
    screen.blit(workstation_img, workstation_img.get_rect(center=goal_center))

def draw_grid(environment, agvPixelSize):
    pixelWidth = environment.pixelWidth
    pixelHeight = environment.pixelHeight
    
    for x in range(0, pixelWidth, agvPixelSize):
        pg.draw.line(screen, LIGHTGRAY, (x, 0), (x, pixelHeight))
    for y in range(0, pixelHeight, agvPixelSize):
        pg.draw.line(screen, LIGHTGRAY, (0, y), (pixelWidth, y))

def vec2int(v):
    return (int(v.x), int(v.y))


listOfAGVs = []
getTileCoordinate = []
obstacles = [(5, 9), (5, 10), (5, 11), (5, 12), (5, 13), (4, 13), (4, 12), (4, 11), (4, 10), (4, 9), (3, 5), (3, 4), (4, 4), (4, 5), (4, 14), (5, 14), (17, 3), (17, 4), (17, 5), (18, 5), (18, 4), (18, 3), (17, 6), (18, 6), (19, 3), (19, 4), (19, 5), (19, 6), (23, 3), (23, 4), (23, 5), (23, 6), (24, 6), (25, 6), (25, 5), (24, 5), (24, 4), (25, 4), (25, 3), (24, 3), (17, 11), (17, 12), (17, 13), (18, 13), (19, 13), (19, 12), (19, 11), (18, 11), (18, 12), (23, 11), (23, 12), (23, 13), (25, 13), (24, 13), (25, 12), (24, 12), (24, 10), (25, 10), (25, 11), (24, 11), (5, 4), (5, 5), (6, 9), (6, 10), (6, 11), (6, 12), (6, 13), (6, 14), (13, 6), (12, 6), (11, 6), (13, 3), (12, 3), (11, 3), (11, 4), (11, 5), (13, 5), (13, 4), (12, 4), (12, 5), (11, 11), (11, 12), (11, 13), (13, 13), (12, 13), (12, 12), (13, 12), (13, 11), (12, 11), (23, 10), (19, 10), (18, 10), (17, 10), (13, 10), (12, 10), (11, 10)]
e = Environment(1280, 640, 32, obstacles, listOfAGVs)
screen = pg.display.set_mode((e.pixelWidth, e.pixelHeight))            
safetyPaddingCorners, safetyPaddingNOCorners = e.calculate_safety_padding()

#task = list of nodes/tiles to visit:
tasks1 = [vec(11, 14),vec(17, 14), vec(23, 14), vec(23, 7), vec(17, 7), vec(11, 7), vec(1, 1)]
astar1 = Astar( vec(12, 15), vec(17, 14), safetyPaddingCorners, safetyPaddingNOCorners)
astar1. safety_padding_costs(safetyPaddingNOCorners)
astar1. safety_padding_costs2(safetyPaddingCorners)
path1,_ = astar1.a_star_search(e)
agv1 = AGV(32, e, path1)
e.listOfAGVs.append(agv1)

for obstacle in obstacles:
    e.obstacles.append(vec(obstacle))

all_sprites = pg.sprite.Group()
all_sprites.add(agv1)


running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
#NOTE: Use left mouse buttom to draw/remove tiles(appear in green)
#press "m" on the keyboard to print coordinates of those tiles.               
            if event.key == pg.K_m:
                # print the coordinates list for saving
                print([(int(loc.x), int(loc.y)) for loc in getTileCoordinate])

        #add/remove tiles:
        if event.type == pg.MOUSEBUTTONDOWN:
            mpos = vec(pg.mouse.get_pos()) // agv1.agvPixelSize 
            if event.button == 1:
                if mpos in getTileCoordinate:
                   getTileCoordinate.remove(mpos)
                else:
                    getTileCoordinate.append(mpos)



    screen.fill(DARKGRAY)

    draw_grid(e, agv1.agvPixelSize)
    draw_path_arrows(path1, astar1.end, astar1.start, agv1.agvPixelSize)
    draw(e.obstacles, astar1.weights, agv1.agvPixelSize)
    draw_icons(e, astar1.start, astar1.end, agv1.agvPixelSize)

    agv_all_paths_list = [] #list of dictionaries with paths(=dictionary) point1-point2, point2-point3... for all tasks given to a particular agv
    for i in range(0,(len(tasks1)-1), 1):
        j = tasks1[i]
        k = tasks1[i+1]
        astar = Astar( j, k, safetyPaddingCorners, safetyPaddingNOCorners)
        astar. safety_padding_costs(safetyPaddingNOCorners)
        astar. safety_padding_costs2(safetyPaddingCorners)
        path,_ = astar.a_star_search(e)
        agv_all_paths_list.append(path)
       
        draw_path_arrows(path, k, j, agv1.agvPixelSize)
        draw_icons(e, j, k, agv1.agvPixelSize)

    
    pg.display.flip()
pg.quit()



