import numpy as np

class Particle(object):
    def __init__(self, numofdim):
        self.x = np.zeros(numofdim, )
        self.v = np.zeros(numofdim, )
        self.pbest = None
        self.pbest_fitness = float('inf')

    def __init__(self, numofdim, low, high):
        self.x = np.random.uniform(low, high, numofdim)
        self.v = np.zeros(numofdim, )
        self.pbest = None
        self.pbest_fitness = float('inf')

class PSO(object):
    def __init__(self, numofdim, numofparticles=5, c1=2, c2=2, numofiter=5):
        self.numofdim = numofdim
        self.numofparticles = 10
        self.c1 = c1
        self.c2 = c2
        self.numofiter = numofiter
        self.f = None

    def initialize_particles(self):
        self.particles = [Particle(self.numofdim) for i in xrange(self.numofparticles)]
    
    def initialize_particles(self, low, high):
        self.particles = [Particle(self.numofdim, low, high) for i in xrange(self.numofparticles)]

    def search(self):
        self.gbest_fitness = float('inf')
        self.gbest = None

        self.initialize_particles(-600, 601)

        for i in xrange(self.numofiter):
            for particle in self.particles:
                fitness = self.f(particle.x)
                if fitness < particle.pbest_fitness:
                    particle.pbest_fitness = fitness
                    particle.pbest = np.copy(particle.x)

                if fitness < self.gbest_fitness:
                    self.gbest_fitness = fitness
                    self.gbest = np.copy(particle.x)

            for particle in self.particles:
                particle.v = particle.v + self.c1 * np.random.rand() * (particle.pbest - particle.x) \
                    + self.c2 * np.random.rand() * (self.gbest - particle.x)
                particle.x += particle.v
            print "Iter: %d Cost: %.4f Sol: " % (i, self.gbest_fitness),
            print self.gbest

    

if __name__ == "__main__":
    pso = PSO(2, numofparticles=5, numofiter=100)
    #Griewangks function
    pso.f = lambda x: np.sum(x ** 2) / 4000 - np.cos(x[0]) * np.cos(x[1] / np.sqrt(2)) + 1
    pso.search()
