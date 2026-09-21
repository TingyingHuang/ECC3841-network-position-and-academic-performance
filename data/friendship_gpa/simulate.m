% ---------------------------------------------------------------------
% Original authors' code, included for reference only. Not modified,
% not used by our own pipeline (see scripts/friendship_gpa/*.py).
% Source: Smirnov, I., & Thurner, S. (2017). PLOS ONE, 12(8): e0183473.
% Data & code: Harvard Dataverse, doi:10.7910/DVN/SZA9YW (CC0 1.0).
% See ../SOURCE.md for the full citation and licence.
% ---------------------------------------------------------------------
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