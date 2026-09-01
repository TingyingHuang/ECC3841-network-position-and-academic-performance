function [networks_sim, gpa_sim] = model(start_network, gpa, steps, ro, m, s)
    networks_sim = {};
    gpa_sim = {};
    networks_sim{1} = start_network;
    gpa_sim{1} = gpa;
    N = size(start_network, 1);
    for i = 2:steps+1
        network = networks_sim{i-1};
        gpa = gpa_sim{i-1};
        todo = zeros(N, 2);
        for ego = 1:N   
            alters = find(network(ego, :));
            if (numel(alters > 0))
                alter = randsample(alters, 1);
                todo(ego, 1) = alter;
                todo(ego, 2) = randi([1,N],1,1);
            end
        end

        for ego = 1:N
            alter = todo(ego, 1); new_alter = todo(ego, 2);
            if alter > 0
                Dold = abs(gpa(alter) - gpa(ego));
                Dnew = abs(gpa(new_alter) - gpa(ego));
                if (Dnew < Dold) || (rand <= ro)
                    network(ego, alter) = 0;
                    network(ego, new_alter) = 1;
                end
            end   
        end
        networks_sim{i} = network;
        gpa_sim{i} = gpa + normrnd(m, s, numel(gpa), 1);
    end
end