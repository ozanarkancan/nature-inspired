#=Simple Genetic Algorithm for one-max problem=#

using PyPlot

#fitness function
one_max(indv) = count(x -> x == 1, indv)

get_fitness_scores(population) = map(x -> one_max(population[x,:]), 1:size(population)[1])

function selection(population, fs)
    function find_place(n, r)
        t = 1.0
        p = 0
        for i=1:length(n)
            if r > t - n[i]
                p = i
                break
            else
                t = t - n[i]
            end
        end
        return p
    end

    tot = sum(fs)
    norm = fs / tot
    n = size(population)[1]
    rands = rand(n, )

    return population[map(x -> find_place(norm, rands[x]), 1:n), :]
end

function crossover!(population, prob)
    n, l = size(population)
    for i=1:n
        if rand() < prob
            parents = rand(1:n, 2,)
            points = rand(1:l, 2,)

            if points[1] < points[2]
                p1 = points[1]
                p2 = points[2]
            else
                p1 = points[2]
                p2 = points[1]
            end

            population[parents[1], p1:p2] = population[parents[2], p1:p2]
        end
    end
end

function mutation!(population, prob)
    n, l = size(population)
    for i=1:n
        if rand() < prob
            point = rand(1:l)
            population[i, point] = population[i, point] $ 1
        end
    end
end

#ARGS
#arg1 l : length of individual
#arg2 n : size of population
#arg3 c_prob : crossover probability
#arg4 m_prob : mutation probability

l = int(ARGS[1])
n = int(ARGS[2])
c_prob = float(ARGS[3])
m_prob = float(ARGS[4])

population = rand(0:1, n, l)

fs = get_fitness_scores(population)

totals = Int64[]
maxs = Int64[]

while !(l in fs)
    append!(totals, [sum(fs)])
    append!(maxs, [maximum(fs)])
    
    population = selection(population, fs)
    crossover!(population, c_prob)
    mutation!(population, m_prob)
    
    fs = get_fitness_scores(population)
end

append!(totals, [sum(fs)])
append!(maxs, [maximum(fs)])

plot(totals, hold=true)
plot(maxs, "x")
title(string("Population Size: ", n, " Length: ", l, " Crossover Prob: ", c_prob, " Mutation Prob: ", m_prob))
xlabel("Iteration")
ylabel("Total Fitness")
savefig("one_max_solution.png")
    
