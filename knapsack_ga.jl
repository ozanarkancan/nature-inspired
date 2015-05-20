#=Genetic Algorithm for 0/1 Knapsack Problem=#

#fitness function
function fitness(indv, vals, weights, capacity)
    tot_ws = sum(weights[findin(indv, 1)])
    if tot_ws > capacity
        return 0
    else
        return sum(vals[findin(indv, 1)])
    end
end

get_fitness_scores(population, vals, weights, capacity) = map(x -> fitness(population[x,:], vals, weights, capacity), 1:size(population)[1])

function tournament_selection(population, fs)
    n, l = size(population)
    mating_pool = zeros(n, l)

    for i=1:n
        indvs = rand(1:n, 2)
        mating_pool[i, :] = population[indvs[findmax(fs[indvs])[2]], :]
    end
    return mating_pool
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
            population[i, point] = int(population[i, point]) $ 1
        end
    end
end

#ARGS
n = int(ARGS[1])
c_prob = float(ARGS[2])
m_prob = float(ARGS[3])
genlimit = int(ARGS[4])

srand(12345)
params = split(readline(STDIN))
l = int(params[1])
capacity = int(params[2])

vals = Int64[]
weights = Int64[]

for i=1:l
    item = split(readline(STDIN))
    append!(vals, [int(item[1])])
    append!(weights, [int(item[2])])
end

population = rand(0:1, n, l)
fs = get_fitness_scores(population, vals, weights, capacity)
gen = 0

while length(unique(fs)) / n > 0.1 && gen < genlimit
    
    population = tournament_selection(population, fs)
    crossover!(population, c_prob)
    mutation!(population, m_prob)
    
    fs = get_fitness_scores(population, vals, weights, capacity)
    gen += 1
end

sol = findmax(fs)
println(sol[1])
solvec = vec(population[sol[2], :])
for i=1:l
    print(int(solvec[i]))
    print(" ")
end
