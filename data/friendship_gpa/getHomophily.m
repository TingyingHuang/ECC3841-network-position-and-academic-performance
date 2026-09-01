function [result, perm_mean, perm_std] = getHomophily(networks, gpa_vector, number_of_permutations)    
    num = numel(networks);
    result = zeros(num,1);
    perm_mean = zeros(num,1);     
    perm_std = zeros(num, 1);
    s = size(gpa_vector, 2);
    if s > 1
        is_changing = 1;
    else
        is_changing = 0;
    end
        
    for i = 1:num
        network = networks{i};
        if is_changing
            gpa = gpa_vector(:, i);
        else
            gpa = gpa_vector;
        end
         
        gpa_friends = network * gpa ./ sum(network, 2);
        gpa_friends(isnan(gpa_friends)) = 0;
        if (sum(gpa_friends > 0) == 0)
            result(i) = -1; continue;
        else
            result(i) = corr(gpa(gpa_friends > 0), gpa_friends(gpa_friends > 0));
        end
        
        if number_of_permutations > 0
            filter = sum(network, 1) > 0 | sum(network, 2)' > 0;
            filtered = gpa(filter);
            err = zeros(number_of_permutations, 1);
            for j = 1:number_of_permutations
                permuted = gpa;
                permuted(filter) = filtered(randperm(numel(filtered)));
                gpa_perm = permuted;
                gpa_friends_perm = network * gpa_perm ./ sum(network, 2);
                gpa_friends_perm(isnan(gpa_friends_perm)) = 0;        
                err(j) = corr(gpa_perm(gpa_friends_perm > 0), gpa_friends_perm(gpa_friends_perm > 0));
            end
            perm_mean(i) = mean(err);
            perm_std(i) = std(err);
        end
    end
end