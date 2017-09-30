function out= Activation(act_func, X)
% Activation Implementation of various activation functions
% Input: act_func string which can be 'sigmoid', 'relu', 'tanh', 'softmax'
% Output: otuput after applying activation
    if (strcmp(act_func,'sig'))
        out = Sigmoid(X);
    elseif (strcmp(act_func,'relu'))
        out = Relu(X);
    elseif (strcmp(act_func,'tanh'))   
        out = Tanh(X);
    elseif (strcmp(act_func,'softmax'))   
        out = Softmax(X);
    else
        fprintf('[ActivationFunction .. BAD][func=%s]\n', act_func);
    end
end

function out = Sigmoid(X)
    out = 1 ./ (1 + exp(-1 * X));
end

function out = Relu(X)
    out = max(X, 0);
end

function out = Tanh(X)
    out = (exp(X) - exp(-1 * X)) ./ (exp(X) + exp(-1 * X));
end

function out = Softmax(X)
    denom = sum(exp(X), 2);
    out = exp(X) ./ denom;
end

