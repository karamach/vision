function [W, b, gamma, beta] = UpdateParameters(W, b, grad_W, grad_b, grad_W_prev, grad_b_prev, grad_gamma, grad_beta, learning_rate, momentum, reg_coeff, gamma, beta, use_bn)
    
    for i = 1:length(W)
        W{i} = W{i} - learning_rate * (grad_W{i} + momentum * grad_W_prev{i} + reg_coeff*W{i});
        b{i} = b{i} - learning_rate * (grad_b{i} + momentum * grad_b_prev{i});
    end
    
    if (use_bn == 1)
        for i = 1:length(W)-1
            gamma{i} = gamma{i} - learning_rate * grad_gamma{i}';
            beta{i} = beta{i} - learning_rate * grad_beta{i}';
        end
    end
end
