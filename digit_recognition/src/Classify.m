function [output] = Classify(W, b, data, gamma, beta, use_bn, act_func)
% Classify Classify the data 
% Input: W is the weights of a pre trained network
%        b is the bias of a pre trained network
%        data is the data to be classified
%        gamma is the batch normalization scale coefficient
%        beta is the batch normalization shift coefficient
%        use_bn is the flag for using batch normalization
%        act_func is the activation function to be used in hidden layer
% Output: Output softmax probabilities for all the classes
    [output, ~, ~] = Forward(W, b, data, gamma, beta, use_bn, act_func);    
end
