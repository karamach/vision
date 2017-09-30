function [W, b, gamma, beta] = TrainEpoch(W, b, train_data, train_label, batch_size, learning_rate, momentum, reg_coeff, gamma, beta, use_bn, act_func)

    avg_grad_W_prev = cell(length(W), 1);
    avg_grad_b_prev = cell(length(W), 1);
    for i =1:length(W)
        avg_grad_W_prev{i} = zeros(size(W{i}));
        avg_grad_b_prev{i} = zeros(size(b{i}));
    end

    perm = randperm(size(train_data,1));    
    for i = 1:batch_size:length(perm)
        upper_limit = min(i-1+batch_size, size(train_data,1));
        idx = perm(i:upper_limit);
        [avg_grad_W, avg_grad_b, grad_gamma, grad_beta] = TrainBatch(W, b, train_data(idx, :), train_label(idx, :), gamma, beta, use_bn, act_func);
        [W, b, gamma, beta] = UpdateParameters(W, b, avg_grad_W, avg_grad_b, avg_grad_W_prev, avg_grad_b_prev, grad_gamma, grad_beta, learning_rate, momentum, reg_coeff, gamma, beta, use_bn);
        avg_grad_W_prev = avg_grad_W;
        avg_grad_b_prev = avg_grad_b;
    end
end

