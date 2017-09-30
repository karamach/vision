function [W, b] = NormalizedInitialization(layers)
% NormalizedInitialization Generates initial values for weight and bias
% Input: layers is a vector of dimensions of the network
% Output: W is the weights of a pre trained network
%         b is the bias of a pre trained network
    rng(5);
    W = cell(length(layers)-1, 1);
    b = cell(length(layers)-1, 1);       
    for layer = 1:length(layers)-1
        max_range = sqrt(6)/sqrt(layers(layer)+layers(layer+1));
        min_range = -max_range;
        W{layer} = (max_range-min_range)*rand(layers(layer), layers(layer+1)) + min_range;
        b{layer} = zeros(1, layers(layer+1));
    end    
end

