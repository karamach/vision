function [g_W, g_b, g_gamma, g_beta] = Backward(W,  X, Y, act_h, act_a, y, x_h, mu, sigm_sq, gamma, beta, use_bn, act_func)
% Backward Implement one pass of back propogation
% Input: W is the weights of the network
%        X is the input data to the network
%        act_h is the set of post activations for all layers
%        act_a is the set of pre activations for all layers
%        y is the set of estimated actications for all nodes after shift
%            and scale
%        x_h is the set of estimated actications for all nodes after normalizing with
%            mean and variance
%        mu is the mean of activations for all nodes
%        sigma_sq is the variance of activations for all nodes
%        gamma is the batch normalization scale coefficient
%        beta is the batch normalization shift coefficient
%        use_bn is the flag for specifying to do batch normalization
%        act_func is the activation function to be used in hidden layer
% Output: g_W is the gradient of weights
%         g_b is the gradient of bias
%         g_gamma is the gradient of batch normalization scale coeff
%         g_beta is the gradient of batch normalization shift coeff
    g_W = cell(length(W), 1);
    g_b = cell(length(W), 1);
    g_gamma = cell(length(W), 1);
    g_beta = cell(length(W), 1);
    
    % output layer gradients
    output_layer_index = length(W);
    g_loss_post_bn_act = act_h{output_layer_index} - Y;         % Cross entropy loss
    g_loss_pre_bn_act = g_loss_post_bn_act;
    g_pre_act_weight = repmat(act_h{output_layer_index-1}, 1, 1, size(act_h{output_layer_index}, 2));
    g_loss_weight = permute(g_loss_pre_bn_act .* permute(g_pre_act_weight, [1,3,2]), [1, 3, 2]);
    g_W{length(W)} = g_loss_weight;     
    g_loss_bias_weight = g_loss_pre_bn_act;
    g_b{output_layer_index} = g_loss_bias_weight;
         
    % Gradients for hidden layers 
    for i = length(W)-1:-1:1
        hidden_layer_index = i;        
        
        g_loss_post_act = g_loss_pre_bn_act * W{hidden_layer_index+1}';    
        g_post_act_pre_act =  ActivationGradient(act_func, act_h{hidden_layer_index});
        g_loss_post_bn_act = g_loss_post_act .* g_post_act_pre_act;
        [g_loss_pre_bn_act, g_gamma{hidden_layer_index}, g_beta{hidden_layer_index}] = ComputeBNGradients(use_bn, g_loss_post_bn_act, x_h{i},  sigm_sq{i}, gamma{i}, size(X, 1));        
        
        prev_layer_act = GetPreviousLayerPostActivation(hidden_layer_index, X, act_a);
        g_pre_act_weight = repmat(prev_layer_act, 1, 1, size(act_h{hidden_layer_index}, 2));
        g_loss_weight = permute(g_loss_pre_bn_act .* permute(g_pre_act_weight, [1,3,2]), [1, 3, 2]);
        
        g_W{hidden_layer_index} = g_loss_weight;
        g_loss_bias_weight = g_loss_pre_bn_act;
        g_b{hidden_layer_index} = g_loss_bias_weight;        
    end    
end


function [prev_act_a] = GetPreviousLayerPostActivation(layer_index, X, act_a)
    if (layer_index == 1)
        prev_act_a = X;
    else
        prev_act_a = act_a{layer_index-1};
    end
end

function [g_loss_pre_bn_act, g_gamma, g_beta] = ComputeBNGradients(use_bn, g_loss_post_bn_act, x_h, sig_sq, gamma, m)
    g_loss_pre_bn_act = g_loss_post_bn_act;
    g_gamma = g_loss_post_bn_act;
    g_beta = g_loss_post_bn_act;
    
    if (use_bn == 1)
        eps = 1e-3;
        den = m*sqrt(sig_sq+eps);
        t1 = m * (g_loss_post_bn_act .* gamma');        
        t2 = sum(g_loss_post_bn_act .* gamma', 1);        
        t3 = x_h .* sum((g_loss_post_bn_act .* gamma') .* x_h, 1);        
        g_loss_pre_bn_act = (t1-t2-t3) ./ den ;
        g_beta = sum(g_loss_post_bn_act, 1);
        g_gamma = sum(g_loss_post_bn_act .* x_h, 1);
    end
end
