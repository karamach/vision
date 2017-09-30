function [output, act_h, act_a, y, x_h, mu, sigm_sq] = Forward(W, b, X, gamma, beta, use_bn, act_func)
% Forward Implements one pass of forward propogation
% Input: W is the weights of a pre trained network
%        b is the bias of a pre trained network
%        X is the training, validation or classification data
%        gamma is the batch normalization scale coefficient
%        beta is the batch normalization shift coefficient
%        use_bn is the flag for using batch normalization
%        act_func is the activation function to be used in hidden layer
% Output: output is the softmax probabilities
%         act_h is the post activations for all layers
%         act_a is the pre activations for all layers
%         x_h is the set of estimated actications for all nodes after normalizing with
%            mean and variance
%         mu is the mean of activations for all nodes
%         sigma_sq is the variance of activations for all nodes
    act_h = cell(length(W), 1);    
    y = cell(length(W), 1);  
    x_h = cell(length(W), 1);  
    mu = cell(length(W), 1);  
    sigm_sq = cell(length(W), 1);  
        
    % Hidden layer
    idx = 1;
    act_a{idx} = X*W{idx} + b{idx};
    [y{idx}, x_h{idx}, mu{idx}, sigm_sq{idx}] = BatchNormalize(act_a{idx}, gamma{idx}, beta{idx}, use_bn);    
    act_h{idx} = Activation(act_func, y{idx});    
    
    for idx = 2:length(W)-1
        act_a{idx} = act_h{idx-1}*W{idx} + b{idx};
        [y{idx}, x_h{idx}, mu{idx}, sigm_sq{idx}] = BatchNormalize(act_a{idx}, gamma{idx}, beta{idx}, use_bn);
        act_h{idx} = Activation(act_func, y{idx}); 
    end

    % Output layer
    idx = length(W);
    act_a{idx} = act_h{idx-1}*W{idx} + b{idx};
    act_h{idx} = Activation('softmax', act_a{idx});
    output = act_h{idx};
end

    


