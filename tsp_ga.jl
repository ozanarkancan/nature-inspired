#=
Solution for tsp by ga
Data rom: http://stackoverflow.com/questions/11007355/data-for-simple-tsp                                                      
Optimal path: 1-8-5-4-10-6-3-7-2-11-9-1 = 253km
=#

using PyPlot

function initialize_population(l, n)
    population = zeros(n, l)
    cities = int(linspace(1, l, l))
    for i=1:n
        population[i,:] = shuffle(cities)
    end
    return population
end

#fitness function
function cost(indv, data)
    path = vec(copy(indv))
    append!(path, [path[1]])
    return sum(map((x, y) -> data[x,y], path[1:(end - 1)], path[2:end]))
end

get_fitness_scores(population, data) = map(x -> cost(population[x,:], data), 1:size(population, 1))

function tournament_selection(population, fs)
    n, l = size(population)
    mating_pool = zeros(n, l)
    
    for i=1:n
        indvs = rand(1:n, 2,)
        mating_pool[i,:] = population[indvs[findmin(fs[indvs])[2]],:]
    end
    return mating_pool
end

#pmx
function crossover!(population, prob)
    n, l = size(population)
    offspring = zeros(n, l)
    for i=1:n
        if rand() < prob
            parents = rand(1:n, 2,)
            point = rand(1:l)

            indv = vec(copy(population[parents[1], 1:point]))
            par2 = vec(copy(population[parents[2], :]))

            for j=(point+1):l
               for k=1:l
                if !(par2[k] in indv[1:(j-1)])
                    append!(indv,[par2[k]])
                    break
                end
               end
            end
            offspring[i, :] = indv
        else
            offspring[i, :] = population[i, :]
        end
    end
    population = offspring
end

#Swap random two points
function mutation!(population, prob)
    n, l = size(population)
    for i=1:n
        if rand() < prob
            points = rand(1:l, 2,)
            tmp = population[i, points[1]]
            population[i, points[1]] = population[i, points[2]]
            population[i, points[2]] = tmp
        end
    end
end

#ARGS
#arg1 n : size of population
#arg2 c_prob : crossover probability
#arg3 m_prob : mutation probability
#args4 genlimit : limit for generation

n = int(ARGS[1])
c_prob = float(ARGS[2])
m_prob = float(ARGS[3])
genlimit = int(ARGS[4])

data = [0   29  20  21  16  31  100 12  4   31  18;
    29  0   15  29  28  40  72  21  29  41  12;
    20  15  0   15  14  25  81  9   23  27  13;
    21  29  15  0   4   12  92  12  25  13  25;
    16  28  14  4   0   16  94  9   20  16  22;
    31  40  25  12  16  0   95  24  36  3   37;
    100 72  81  92  94  95  0   90  101 99  84;
    12  21  9   12  9   24  90  0   15  25  13;
    4   29  23  25  20  36  101 15  0   35  18;
    31  41  27  13  16  3   99  25  35  0   38;
    18  12  13  25  22  37  84  13  18  38  0]

l = size(data, 1)
population = initialize_population(l, n)

fs = get_fitness_scores(population, data)

#println("Initial: ")
#println(population)
#println(fs)

avgs = Float64[]
mins = Float64[]
gen = 0

@time while !(253 in fs) && gen < genlimit
    append!(avgs, [sum(fs) / length(fs)])
    append!(mins, [minimum(fs)])
    population = tournament_selection(population, fs)
    crossover!(population, c_prob)
    mutation!(population, m_prob)
    
    fs = get_fitness_scores(population, data)
    gen += 1
end

println(string("Gen: ", gen))
println(string("Sol : ", population[findin(fs, 253), :]))

append!(avgs, [sum(fs) / length(fs)])
append!(mins, [minimum(fs)])

plot(avgs, hold=true)
plot(mins, "x")
title(string("Population Size: ", n, " Crossover Prob: ", c_prob, " Mutation Prob: ", m_prob))
xlabel("Iteration")
ylabel("Avg Fitness")
savefig("tsp_ga_solution.png")
    
