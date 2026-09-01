%% Load data and compute homophily index
clear all;
load('data.mat');

[homophily_seniors, homophily_randomized_mean, homophily_randomized_std] = getHomophily(networks_seniors, gpa_seniors, 100);
homophily_juniors = getHomophily(networks_juniors, gpa_juniors, 0);
homophily_sophomores = getHomophily(networks_sophomores, gpa_sophomores, 0);
homophily_freshmen = getHomophily(networks_freshmen, gpa_freshmen, 0);
gpa_average = (gpa_school(:,1) + gpa_school(:,2) + gpa_school(:,3) + gpa_school(:,5)) / 4;
[homophily_school, homophily_school_randomized_mean, homophily_school_randomized_std]= getHomophily(networks_school, gpa_average, 100);
homophily_school_coevolv = getHomophily(networks_school, gpa_school, 0);

%% Run model to simulate results
[homophily_seniors_sim_mean, homophily_seniors_sim_std] = simulate(networks_seniors{1}, gpa_seniors, 14, 0.58, 10);
[homophily_juniors_sim_mean, homophily_juniors_sim_std] = simulate(networks_juniors{1}, gpa_juniors, 10, 0.61, 10);
[homophily_sophomores_sim_mean, homophily_sophomores_sim_std] = simulate(networks_sophomores{1}, gpa_sophomores, 6, 0.60, 10);
[homophily_school_sim_mean, homophily_school_sim_std] = simulate(networks_school{1}, gpa_average, 6, 0.55, 10);

%% Plot university 
close all;
figure(1)
m_size = 18;
tck_size = 12;

errorbar(homophily_seniors_sim_mean, homophily_seniors_sim_std, 's-b', 'MarkerSize', m_size, 'LineWidth', 2, 'MarkerFaceColor', 'w');hold on;
errorbar(5:14,homophily_juniors_sim_mean, homophily_juniors_sim_std, 's-r', 'MarkerSize', m_size,  'LineWidth', 2, 'MarkerFaceColor', 'w');hold on;
errorbar(9:14,homophily_sophomores_sim_mean, homophily_sophomores_sim_std, 's-r', 'Color', [0, 100,0]/255,'MarkerSize', m_size,'LineWidth', 2, 'MarkerFaceColor', 'w');hold on;

h1 = plot(homophily_seniors, 'bx', 'MarkerSize', m_size, 'LineWidth', 2); hold on;
h2 = plot(5:14, homophily_juniors,'rx', 'MarkerSize', m_size, 'LineWidth', 2); hold on;
h3 = plot(9:14, homophily_sophomores, 'x', 'MarkerSize', m_size, 'LineWidth', 2,'Color', [0,100,0]/255); hold on;
h4 = plot(13:14, homophily_freshmen,'x', 'MarkerSize', m_size, 'LineWidth', 2,'Color', [255,100,50]/255);
h5 = errorbar(homophily_randomized_mean, homophily_randomized_std, 'kv', 'MarkerSize', m_size-4, 'MarkerFaceColor', 'w', 'LineWidth', 1);hold on;
legend([h1 h2 h3 h4 h5], {'seniors', 'juniors', 'sophomores', 'freshmen', 'randomized'}, 'Location', 'NorthWest');

ylim([-0.1 0.6]);
xlim([-2 15]);

set(gca, 'YTick', 0:0.1:0.4);
set(gca, 'YTickLabel', {'0','   0.1', '0.2', '0.3','0.4'});
ylabel('Homophily Index')
set(gca, 'XTick', 1:14);
set(gca, 'XTickLabel', {'1 Dec ''12','1 Mar ''13','1 Jun ''13','1 Sep ''13','1 Dec ''13','1 Mar ''14','1 Jun ''14','1 Sep ''14','1 Dec ''14','1 Mar ''15','1 Jun ''15','1 Sep ''15','1 Dec ''15', '1 Mar ''16'});
set(gca, 'XTickLabelRotation', 60);
set(gca,'fontsize',tck_size);

%% Plot school
figure(2)
h1 = errorbar(homophily_school_sim_mean, homophily_school_sim_std, 's-b', 'MarkerSize', m_size, 'LineWidth', 2, 'MarkerFaceColor', 'w');hold on;
h2 = plot(homophily_school, 'bx', 'MarkerSize', m_size, 'LineWidth', 2); hold on;
h3 = plot(homophily_school_coevolv,'ro', 'MarkerSize', m_size, 'LineWidth', 2); hold on;
h4 = errorbar(homophily_school_randomized_mean, homophily_school_randomized_std, 'kv', 'MarkerSize', m_size-4, 'MarkerFaceColor', 'w', 'LineWidth', 1);hold on;
legend([h1, h2, h3, h4], {'model', 'data: fixed', 'data: coevolution', 'randomized'}, 'Location', 'NorthWest');

ylim([-0.1 0.6]);
xlim([0 7]);

set(gca, 'YTick', 0:0.1:0.4);
set(gca, 'YTickLabel', {'0','   0.1', '0.2', '0.3','0.4'});
ylabel('Homophily Index')
set(gca, 'XTick', 1:6);
set(gca, 'XTickLabel', {'1 Dec ''14','1 Mar ''15','1 Jun ''15','1 Sep ''15','1 Dec ''15', '1 Mar ''16'});
set(gca, 'XTickLabelRotation', 60);
set(gca,'fontsize',tck_size);

