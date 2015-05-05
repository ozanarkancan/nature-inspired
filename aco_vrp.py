import numpy as np
import matplotlib.pyplot as plt
import sys

def euc_2d(p1, p2):
    return np.sqrt(np.sum((p1 - p2) ** 2))

class Problem(object):
    def __init__(self, data, ro, alpha, beta):
        self.dist = data['dist']
        self.numofcities = data['N']
        self.ro = ro
        self.alpha = alpha
        self.beta = beta
        self.Q = data['c']
        self.qs = data['qs']
        self.rstate = np.random.RandomState(1234)
        
        tot = np.sum(map(lambda i: self.dist[0, i], range(1, self.numofcities)))
        self.tau_min = self.Q / (2 * tot)
        self.tau_max = self.Q / tot
        self.tau = np.ones((self.numofcities, self.numofcities)) * self.rstate.uniform(self.tau_min, self.tau_max)
        self.global_tabu_list = []

class Ant(object):
    def __init__(self, problem):
        self.problem = problem
        self.tabu_list = [0]
        self.route = [0]
        self.filled_capacity = 0

    def next_city(self):
        cand_temp = self.candidates[:]
        for j in cand_temp:
            if self.problem.qs[j] + self.filled_capacity > self.problem.Q:
                self.candidates.remove(j)
        
        i = self.route[-1]
        if len(self.candidates) > 0:          
            probs = [np.power(self.problem.tau[i, j], self.problem.alpha) *
                np.power(1.0 / self.problem.dist[i, j], self.problem.beta)
                for j in self.candidates]
       
            probs = probs / np.sum(probs)
            next = self.candidates[np.argmax(probs)]
            self.filled_capacity += self.problem.qs[next]
            
            self.route.append(next)
            self.tabu_list.append(next)
            self.problem.global_tabu_list.append(next)
            self.candidates.remove(next)

    def find_solution(self):
        self.candidates = range(1, self.problem.numofcities)
        [self.candidates.remove(x) for x in self.problem.global_tabu_list]
        
        if len(self.candidates) != 0:#chose first city randomly
            indx = self.problem.rstate.randint(len(self.candidates))
            city = self.candidates[indx]
            self.route.append(city)
            self.tabu_list.append(city)
            self.problem.global_tabu_list.append(city)
            self.candidates.remove(city)
            self.filled_capacity += self.problem.qs[city]

        while len(self.tabu_list) != self.problem.numofcities and self.filled_capacity < self.problem.Q and len(self.candidates) != 0:
            self.next_city()

    def has_edge(self, i, j):
        tour = self.route + [0]
        if i in tour:
            indx = tour.index(i)
            return tour[indx + 1] == j
        else:
            return False

    def cost(self):
        tour = self.route + [0]
        return np.sum(map(lambda i, j: self.problem.dist[i, j], tour[:-1], tour[1:]))

    def local_search(self):
        improvement = False
        
        min_cost = self.cost()
        base_path = self.route[:]
        min_path = self.route[:]

        for i in xrange(1, len(self.route) - 1):
            for j in xrange((i + 1), len(self.route)):
                curr_path = base_path[:]
                curr_path[i] = base_path[j]
                curr_path[j] = base_path[i]
                self.route = curr_path
                curr_cost = self.cost()
                
                if curr_cost < min_cost:
                    min_cost = curr_cost
                    min_path = curr_path[:]
                    improvement = True
        
        self.route = min_path[:]
        if improvement:
            self.local_search()
    
    def tau(self, i, j):
        D = self.cost()
        return (D - self.problem.dist[i, j]) / ((len(self.route) - 1) * D)

    def print_tour(self):
        for x in self.route:
            print x,
            print " ",
        print "0"


class AntOpt(object):
    def __init__(self, data, numiter = 100, ro = 0.9, alpha = 10, beta = 1):
        self.numofants = data['V']
        self.numiter = numiter
        self.problem = Problem(data, ro, alpha, beta)

    def initialize_ants(self):
        self.ants = [Ant(self.problem) for i in xrange(self.numofants)]

    def update_tau(self):
        K = 0
        L = 0.0
        for ant in self.ants:
            if len(ant.route) > 1:
                K += 1
                L += ant.cost()

        for i in xrange(self.problem.numofcities):
            for j in xrange(self.problem.numofcities):
                if i != j:
                    tot = 0.0
                    for ant in self.ants:
                        if ant.has_edge(i, j):
                            ant_cost = ant.cost()
                            tot += (self.problem.Q / (K * L)) * ant.tau(i, j)

                    new_tau = self.problem.ro * self.problem.tau[i, j] + tot

                    if new_tau < self.problem.tau_min:
                        new_tau = self.problem.tau_min
                    elif new_tau > self.problem.tau_max:
                        new_tau = self.problem.tau_max

                    self.problem.tau[i, j] = new_tau

    def generate_solution(self):
        i = 0
        while len(self.problem.global_tabu_list) != (self.problem.numofcities - 1):
            self.problem.global_tabu_list = []
            self.initialize_ants()
            for ant in self.ants:
                ant.find_solution()
            i += 1
            if i == 10:
                break
                    
    def search(self, display=True):
        min_cost = float('inf')
        best_ants = []
        for i in xrange(self.numiter):
            self.generate_solution()
            
            for ant in self.ants:
                ant.local_search()
            
            self.update_tau()
            self.problem.global_tabu_list = []
            cost = np.sum([ant.cost() for ant in self.ants])

            if cost < min_cost:
                min_cost = cost
                best_ants = self.ants[:]

            if display:
                print "\nIter: %d" % (i + 1)
                print "Cost: %f" % cost
            
                for ant in self.ants:
                    ant.print_tour()
        
        print min_cost
        for ant in best_ants:
            ant.print_tour()
            #print ant.filled_capacity

        
def get_data(data_file):
    f = open(data_file, 'r')
    lines = f.readlines()
    data = {}
    info = lines[0].split()
    f.close()
    data['N'] = int(info[0])
    data['V'] = int(info[1])
    data['c'] = float(info[2])
    graph = np.zeros((data['N'], 2))
    data['qs'] = np.zeros((data['N'], ))
    data['dist'] = np.zeros((data['N'], data['N']))

    for i in xrange(data['N']):
        info = lines[i + 1].split()
        data['qs'][i] = float(info[0])
        graph[i, 0] = float(info[1])
        graph[i, 1] = float(info[2])
    
    for i in xrange(data['N']):
        for j in xrange(data['N']):
            if i != j:
                data['dist'][i, j] = euc_2d(graph[i, :], graph[j, :])
    return data

def get_params():
    f = open('config.txt', 'r')
    lines = f.readlines()
    f.close()
    params = {}
    params['numiter'] = int(lines[0].split()[1])
    params['alpha'] = float(lines[1].split()[1])
    params['beta'] = float(lines[2].split()[1])
    params['ro'] = float(lines[3].split()[1])
    return params

if __name__ == "__main__":
    data_file = sys.argv[1]
    data = get_data(data_file)
    params = get_params()
    colony = AntOpt(data, numiter = params['numiter'], 
        alpha = params['alpha'], beta = params['beta'], ro = params['ro'])
    colony.search(display=False)
