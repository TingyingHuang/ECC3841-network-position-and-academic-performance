function [model_mean, model_std] = simulate(network, gpa, steps, theta, iterations) 
    simultation = zeros(steps, iterations);
    for i = 1:iterations
        networks_sim = model(network, gpa, steps - 1, theta, 0, 0);
        homophily_simulation = getHomophily(networks_sim, gpa, 0);
        simulation(:, i) = homophily_simulation;        
    end
    model_mean = mean(simulation');
    model_std = std(simulation');  
end