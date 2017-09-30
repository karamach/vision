function out= ActivationGradient(act_func, X)
% ActivationGradient Compute activation gradient to X based on act_func
% Input: act_func string which can be 'sigmoid', 'relu', 'tanh', 'softmax'
%        X input whose gradient is to be computed
% Output: otuput Activation gradient of X for given activation function
    if (strcmp(act_func,'sig'))
        out = X .* (1 - X);
    elseif (strcmp(act_func,'relu'))
        out = X > 0;
    elseif (strcmp(act_func,'tanh'))   
        out = 1 - X .* X;
    else
        out = X;
    end
end