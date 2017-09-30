function [avg_grad_W, avg_grad_b, grad_gamma, grad_beta] = TrainBatch(W, b, batch_data, batch_label, gamma, beta, use_bn, act_func)
    
    [~, act_h, act_a, y, x_h, mu, sigm_sq] = Forward(W, b, batch_data, gamma, beta, use_bn, act_func);
    [grad_W, grad_b, grad_gamma, grad_beta] = Backward(W, batch_data, batch_label, act_h, act_a, y, x_h, mu, sigm_sq, gamma, beta, use_bn, act_func);          

    avg_grad_W = cell(length(W), 1);
    avg_grad_b = cell(length(W), 1);
    for i =1:length(W)
        avg_grad_W{i} = squeeze(sum(grad_W{i}, 1)/size(batch_data, 1));
        avg_grad_b{i} = sum(grad_b{i}, 1)/size(batch_data, 1);
    end
end


