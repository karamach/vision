function [gamma, beta] = BNInitialization(layers)
% BNInitialization Initialize batch normalization coefficients
% Input: layers is dimensions of the layers in the net
% Output: gamma is the scale coefficient
%         beta is the shift coefficient
    gamma = cell(length(layers)-1, 1);
    beta = cell(length(layers)-1, 1);
    for layer = 1:length(layers)-1
        gamma{layer} = rand(layers(layer+1), 1)/10000;
        beta{layer} = rand(layers(layer+1), 1)/10000;
    end    
end
