import numpy as np
import sys

class Warehouse(object):
    def __init__(self, id, problem):
        self.id = id
        self.problem = problem
        self.customers = []
        self.filled_capacity = 0

    def cost(self):
        c = 0
        if len(self.customers) > 0:
            c += self.problem.s[self.id]
            c += np.sum(self.problem.t[i, self.id] for i in self.customers)
        return c

class Problem(object):
    def __init__(self, data, ro, ro_prime, alpha, beta, gama, theta, q0, q0_prime):
        self.N = data['N']
        self.M = data['M']
        self.ro = ro
        self.ro_prime = ro_prime
        self.alpha = alpha
        self.beta = beta
        self.gama = gama
        self.theta = theta
        self.q0 = q0
        self.q0_prime = q0_prime
        self.caps = np.array(data['caps'])
        self.s = np.array(data['s']) + 1e-6
        self.d = np.array(data['d']) + 1e-6
        self.t = data['t'] + 1e-6
        self.rstate = np.random.RandomState(1234)
        
        heuristic_caps = int(np.floor(np.sum(self.d) / (np.sum(self.caps) / self.N)))
        heuristic_establishing = int(np.floor(np.sum(self.d) / (np.sum(self.s) / self.N)))
        self.ant_cons_heuristic = np.max([heuristic_caps, heuristic_establishing])

        self.tau = self.caps / self.s
        self.ita = self.caps / self.s
        self.ksi = 0.1 / self.t
        self.psi = 1 / self.t

        self.tau_0 = 1. / np.array(self.s)
        self.ksi_0 = self.rstate.rand() * 0.001

class Ant(object):
    def __init__(self, problem):
        self.problem = problem
        self.warehouses = {}
        self.tabu_list = []
        self.r = self.problem.rstate.uniform(self.problem.ant_cons_heuristic, self.problem.N)
        self.r = 2 if self.r < 1 else self.r
        self.generation = 0
    
    def set_number_of_warehouses(self):
        randint = self.problem.rstate.randint(0, self.r)
        self.p = self.problem.ant_cons_heuristic + randint

    def select_warehouses(self):
        candidates = range(self.problem.N)
        for i in xrange(self.p):
            vals = [np.power(self.problem.tau[j], self.problem.alpha) * \
                np.power(self.problem.ita[j], self.problem.beta) for j in candidates]
            q = self.problem.rstate.uniform(0, 1)
            next = -1
            if q <= self.problem.q0:
                next = candidates[np.argmax(vals)]
                candidates.remove(next)
            else:
                probs = vals / np.sum(vals)
            
                tot = 0
                rand = self.problem.rstate.rand()
            
                for i in xrange(len(probs)):
                    tot += probs[i]
                    if rand <= tot:
                        next = candidates[i]
                        candidates.remove(next)
                        break

            self.warehouses[next] = Warehouse(next, self.problem)
            self.tabu_list.append(next)
            if len(candidates) == 0:
                break

    def assign_customers(self):
        customers = range(self.problem.M)
        self.problem.rstate.shuffle(customers)
        for i in customers:
            candidates = []
            for w in self.tabu_list:
                if self.warehouses[w].filled_capacity + self.problem.d[i] < self.problem.caps[self.warehouses[w].id]:
                    candidates.append(self.warehouses[w].id)

            vals = [np.power(self.problem.ksi[i, j], self.problem.gama) * \
                np.power(self.problem.psi[i, j], self.problem.theta) for j in candidates]

            if len(vals) == 0:
                self.tabu_list = []
                self.warehouses = {}
                self.find_solution()
                return

            q = self.problem.rstate.uniform(0, 1)
            
            w = -1
            if q <= self.problem.q0_prime:
                w = candidates[np.argmax(vals)]
            else:
                probs = vals / np.sum(vals)
                tot = 0
                rand = self.problem.rstate.rand()

                for k in xrange(len(probs)):
                    tot += probs[k]

                    if rand <= tot:
                        w = candidates[k]
                        break

            self.warehouses[w].customers.append(i)
            self.warehouses[w].filled_capacity += self.problem.d[i]

    def update_pheromone(self):
        for w in self.tabu_list:
            self.problem.tau[w] = (1 - self.problem.ro) * self.problem.tau[w] + \
                self.problem.ro * self.problem.tau_0[w]

            for i in self.warehouses[w].customers:
                self.problem.ksi[i, w] = (1 - self.problem.ro_prime) * self.problem.ksi[i, w] + \
                    self.problem.ro_prime * self.problem.ksi_0

    def find_solution(self):
        if self.generation > 20:
            return
        self.generation += 1
        self.set_number_of_warehouses()
        self.select_warehouses()
        self.assign_customers()

    def cost(self):
        c = np.sum([self.warehouses[w].cost() for w in self.tabu_list])
        return c

    def print_solution(self):
        customers = ["" for i in xrange(self.problem.M)]
        for w in self.tabu_list:
            for c in self.warehouses[w].customers:
                customers[c] = str(w)
        print self.cost()
        print " ".join(customers)

    def isfeasible(self):
        for c in range(self.problem.M):
            found = False
            for w in self.tabu_list:
                if c in self.warehouses[w].customers:
                    found = True
                    break
            if not found:
                return False
        return True
                

class AntOpt(object):
    def __init__(self, problem, numofants = 10, numiter = 100):
        self.numofants = numofants
        self.numiter = numiter
        self.problem = problem

    def initialize_ants(self):
        self.ants = [Ant(self.problem) for i in xrange(self.numofants)]

    def update_pheromone(self):
        tot_tau = np.zeros(self.problem.N, )
        tot_ksi = np.zeros((self.problem.M, self.problem.N))

        for w in range(self.problem.N):
            for ant in [self.global_best, self.iteration_best]:
                if w in ant.tabu_list:
                    val = (2 * self.iteration_worst.cost() - self.global_best.cost() - \
                        self.iteration_best.cost()) / self.iteration_worst.cost()
                    tot_tau[w] += val * len(ant.warehouses[w].customers)
                    for c in ant.warehouses[w].customers:
                        tot_ksi[c, w] += val

    def generate_solutions(self):
        self.initialize_ants()
        for ant in self.ants:
            try:
                ant.find_solution()
                ant.update_pheromone()#local update
            except:
                pass

    def search(self, display=True):
        self.min_cost = float('inf')
        for i in xrange(self.numiter):
            self.generate_solutions()
            costs = [ant.cost() for ant in self.ants]
            indx = np.argmin(costs)
            self.iteration_best = self.ants[indx]
            self.iteration_worst = self.ants[np.argmax(costs)]
            
            if costs[indx] < self.min_cost:
                self.global_best = self.iteration_best
                self.min_cost = costs[indx]
            
            self.update_pheromone()
            
            if display:
                print "Iteration: %d Cost: %.4f" % (i, self.min_cost)
                self.global_best.print_solution()
                print ""

        self.global_best.print_solution()
        
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
    params['gama'] = float(lines[3].split()[1])
    params['theta'] = float(lines[4].split()[1])
    params['ro'] = float(lines[5].split()[1])
    params['ro_prime'] = float(lines[6].split()[1])
    params['q0'] = float(lines[7].split()[1])
    params['q0_prime'] = float(lines[8].split()[1])
    params['numofants'] = int(lines[9].split()[1])
    return params

if __name__ == "__main__":
    data_file = sys.argv[1]
    data = get_data(data_file)
    #print data
    params = get_params()
    problem = Problem(data=data, ro=params['ro'], ro_prime=params['ro_prime'], \
        alpha=params['alpha'], beta=params['beta'], gama=params['gama'], theta=params['theta'], \
        q0=params['q0'], q0_prime=params['q0_prime'])
    colony = AntOpt(problem, numiter = params['numiter'], numofants = params['numofants'])
    colony.search(display=False)
