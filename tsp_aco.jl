#=
Solving tsp with Ant colony optimization
berlin52 data from TSPLIB
Optimal cost: 7542
=#

#using PyPlot

euc_2d(p1, p2) = sqrt(sum((p1 - p2).^2))

function cost(path, cities)
    indx_dist(i1, i2) = euc_2d(cities[i1, :], cities[i2, :])
    return sum(map(indx_dist, path[1:(end - 1)], path[2:end]))
end

function heuristic_value(data)
    m = size(data, 1)
    val = zeros(m,m)
    for i=1:m
        for j=1:m
            val[i, j] = 1.0 / euc_2d(data[i,:], data[j,:])
        end
    end
    return val
end

function calculate_probs(tabu_list, τ, η, α, β, t)
    i = tabu_list[end]
end

#ARGS

max_it = 100
num_ants = 10
alpha = 2
beta = 2

berlin52 = [565 575; 25 185; 345 750; 945 685; 845 655; 880 660;
25 230; 525 1000; 580 1175; 650 1130; 1605 620; 1220 580; 1465 200;
1530 5; 845 680; 725 370; 145 665; 415 635; 510 875; 560 365; 300 465;
520 585; 480 415; 835 625; 975 580; 1215 245; 1320 315; 1250 400; 
660 180; 410 250; 420 555; 575 665; 1150 1160; 700 580; 685 595;
685 610; 770 610; 795 645; 720 635; 760 650; 475 960; 95 260; 875 920;
700 500; 555 815; 830 485; 1170 65; 830 610; 605 625; 595 360; 1340 725; 1740 245]
