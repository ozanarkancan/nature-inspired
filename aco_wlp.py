import numpy as np
import sys

class Problem(object):
    def __init__(self, data, ro, alpha, beta):
        self.N = data['N']
        self.M = data['M']
        self.ro = ro
        self.alpha = alpha
        self.beta = beta
        self.caps = data['caps']
        self.s = data['s']
        self.d = data['d']
        self.t = data['t']
        self.rstate = np.random.RandomState(1234)
        
        tot = np.sum(self.t)
        self.Q = np.sum(self.caps) / self.N
        #print "Q: %.4f" % self.Q
        self.tau_min = self.Q / (2 * tot)
        #print "Tau Min: %.4f" % self.tau_min
        self.tau_max = self.Q / tot
        #print "Tau Max: %.4f" % self.tau_max
        self.tau = np.ones((self.M, self.N)) * self.rstate.uniform(self.tau_min, self.tau_max)
        self.global_tabu_list = []

class Ant(object):
    def __init__(self, problem, id):
        self.id = id
        self.problem = problem
        self.tabu_list = []
        self.filled_capacity = 0

    def next_city(self):
        cand_temp = self.candidates[:]
        for j in cand_temp:
            if self.problem.d[j] + self.filled_capacity > self.problem.caps[self.id]:
                self.candidates.remove(j)
        
        j = self.id
        if len(self.candidates) > 0:          
            probs = [np.power(self.problem.tau[i, j], self.problem.alpha) *
                np.power(1.0 / self.problem.t[i, j], self.problem.beta)
                for i in self.candidates]
       
            probs = probs / np.sum(probs)
            next = self.candidates[np.argmax(probs)]

            self.filled_capacity += self.problem.d[next]
            self.tabu_list.append(next)
            self.problem.global_tabu_list.append(next)
            self.candidates.remove(next)

    def find_solution(self):
        self.candidates = range(self.problem.M)
        [self.candidates.remove(x) for x in self.problem.global_tabu_list]
        
        if len(self.candidates) != 0:#chose first city randomly
            indx = self.problem.rstate.randint(len(self.candidates))
            city = self.candidates[indx]
            self.tabu_list.append(city)
            self.problem.global_tabu_list.append(city)
            self.candidates.remove(city)
            self.filled_capacity += self.problem.d[city]

        while len(self.tabu_list) != self.problem.M and self.filled_capacity < self.problem.caps[self.id] and len(self.candidates) != 0:
            self.next_city()

    def tau(self):
        return np.sum(map(lambda i: self.problem.t[i, self.id], self.tabu_list))

    def cost(self):
        c = 0
        if len(self.tabu_list) > 0:
            c += self.problem.s[self.id]
            c += self.tau()
        return c

    #def local_search(self):
    #    improvement = False
    #    
    #    min_cost = self.cost()
    #    base_path = self.route[:]
    #    min_path = self.route[:]

     #   for i in xrange(1, len(self.route) - 1):
     #       for j in xrange((i + 1), len(self.route)):
      #          curr_path = base_path[:]
       #         curr_path[i] = base_path[j]
        #        curr_path[j] = base_path[i]
         #       self.route = curr_path
          #      curr_cost = self.cost()
           #     
            #    if curr_cost < min_cost:
             #       min_cost = curr_cost
              #      min_path = curr_path[:]
               #     improvement = True
        
        #self.route = min_path[:]
        #if improvement:
        #    self.local_search()


class AntOpt(object):
    def __init__(self, data, numiter = 100, ro = 0.9, alpha = 10, beta = 1):
        self.numofants = data['N']
        self.numiter = numiter
        self.problem = Problem(data, ro, alpha, beta)

    def initialize_ants(self):
        self.ants = [Ant(self.problem, i) for i in xrange(self.numofants)]

    def update_tau(self):
        K = 0.0
        L = 0.0
        for ant in self.ants:
            if len(ant.tabu_list) > 0:
                K += 1
                L += ant.tau()

        for i in xrange(self.problem.M):
            for j in xrange(self.problem.N):
                l = len(self.ants[j].tabu_list)
                l = 0.00001 if l == 0 else l
                tot = (self.ants[j].tau() - self.problem.t[i, j]) / (l * self.ants[j].tau())
                    
                tot = (self.problem.Q / (K * L)) * np.abs(tot)
                new_tau = self.problem.ro * self.problem.tau[i, j] + tot
                #print "New Tau: %f" % new_tau
                    
                if new_tau < self.problem.tau_min:
                    new_tau = self.problem.tau_min
                elif new_tau > self.problem.tau_max:
                    new_tau = self.problem.tau_max

                self.problem.tau[i, j] = new_tau

    def generate_solution(self):
        i = 0
        while len(self.problem.global_tabu_list) != self.problem.M:
            self.problem.global_tabu_list = []
            self.initialize_ants()
            self.problem.rstate.shuffle(self.ants)
            for ant in self.ants:
                ant.find_solution()
            i += 1
            if i == 10:
                break
    
    def print_solution(self, ants):
        ws = ["" for x in xrange(self.problem.M)]
        for ant in ants:
            for c in ant.tabu_list:
                ws[c] = str(ant.id)
        print " ".join(ws)

    def search(self, display=True):
        self.min_cost = float('inf')
        self.best_ants = []
        for i in xrange(self.numiter):
            self.generate_solution()
            
            #for ant in self.ants:
            #    ant.local_search()
            
            self.update_tau()
            self.problem.global_tabu_list = []
            cost = np.sum([ant.cost() for ant in self.ants])

            if cost < self.min_cost:
                self.min_cost = cost
                self.best_ants = self.ants[:]

            if display:
                print "\nIter: %d" % (i + 1)
                print "Cost: %f" % cost
                self.print_solution(self.ants)
        
        print self.min_cost
        self.print_solution(self.best_ants)
        #for ant in self.best_ants:
        #    print "Ant: %d Cap: %f" % (ant.id, ant.filled_capacity)
        
def get_data(data_file):
    f = open(data_file, 'r')
    lines = f.readlines()
    data = {}
    info = lines[0].split()
    f.close()
    data['N'] = int(lines[0].split()[0])
    data['M'] = int(lines[0].split()[1])
    data['caps'] = []
    data['s'] = []
    data['d'] = []
    data['t'] = np.zeros((data['M'], data['N']))

    for i in xrange(1, data['N'] + 1):
        data['caps'].append(float(lines[i].split()[0]))
        data['s'].append(float(lines[i].split()[1]))

    for i in xrange(data['M']):
        data['d'].append(float(lines[data['N'] + 1 + (2 * i)]))
        data['t'][i, :] = np.array(map(float, lines[data['N'] + 1 + (2 * i) + 1].split()))

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
    #print data
    params = get_params()
    colony = AntOpt(data, numiter = params['numiter'], 
        alpha = params['alpha'], beta = params['beta'], ro = params['ro'])
    colony.search(display=False)
