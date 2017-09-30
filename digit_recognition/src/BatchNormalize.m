function [y, x_h, mu, sigma_sq] = BatchNormalize(x, gamma, beta, use_bn)
    y = x;
    x_h = cell(length(y), 1);  
    mu = cell(length(y), 1);  
    sigma_sq = cell(length(y), 1);      
    if (use_bn == 1)
        epsilon = 1e-3;
        mu = sum(x, 1)/size(x, 1);
        sigma_sq = sum((x-mu) .* (x-mu), 1)/size(x, 1);
        x_h = (x - mu) ./ (sqrt(sigma_sq+epsilon));
        y = gamma' .* x_h + beta';
    end
end