% Check gradient by doing a forward prop by modifying a particular weight
% and validate if the gradient makes sense.

% Initialze classes, layers and epsilon
classes = 26;
layers = [32*32, 400, classes];
learning_rate = 0.01;
epsilon = .0001;
num_samples = 10;
check_threshold = .00000001;

% Load some training data
load('../data/nist26_train.mat', 'train_data', 'train_labels');
num_iter = 90;

% Initialize the network
[W, b] = InitializeNetwork(layers);

% Train the network for some data to get some weights
[W, b] = Train(W, b, train_data(1:num_iter, :), train_labels(1: num_iter, :), learning_rate);

% Do one forward prop
data_vector = train_data(num_iter+1, :);
label_vector = train_labels(num_iter+1, :);
[output, act_h, act_a] = Forward(W, b, data_vector');     

% Do one backprop
[grad_W, grad_b] = Backward(W, b, data_vector', label_vector', act_h, act_a);

% Weights gradient check
for layer_idx=1:length(W)
    % Randomly pick a few weights in the hidden layer and check gradient
    weight_rows = randperm(size(W{layer_idx}, 1), num_samples);
    weight_cols = randperm(size(W{layer_idx}, 2), num_samples);

    num_failures = 0;
    for idx=1:num_samples

        i = weight_rows(idx);
        j = weight_cols(idx);

        % Compute loss for weight - epsilon
        original_weight = W{layer_idx}(i, j);
        W{layer_idx}(i, j) = W{layer_idx}(i, j) - epsilon;
        [~, ~, ~] = Forward(W, b, data_vector');     
        [accuracy_minusepsilon, loss_minusepsilon] = ComputeAccuracyAndLoss(W, b, data_vector, label_vector);

        % Compute loss for weight + epsilon
        W{layer_idx}(i, j) = W{layer_idx}(i, j) + 2*epsilon;
        [output, act_h, act_a] = Forward(W, b, data_vector');     
        [accuracy_plusepsilon, loss_plusepsilon] = ComputeAccuracyAndLoss(W, b, data_vector, label_vector);

        % Validate gradient
        gradient_approx = (loss_plusepsilon - loss_minusepsilon)/(2*epsilon);
        gradient_backprop = grad_W{layer_idx}(i, j);

        if (abs(gradient_approx - gradient_backprop) > check_threshold)
            fprintf('Gradient check failed for weight index %.5f, %.5f, %10f, %10f\n', i, j, gradient_approx, gradient_backprop);
            num_failures = num_failures + 1;
        end

        % Reset weight.
        W{layer_idx}(i, j) = original_weight;
    end
    fprintf('Num failures for weights in layer %1d is %1d out of %1d samples\n', layer_idx, num_failures, num_samples);
end
fprintf('\n');

% Bias gradient check
for layer_idx=1:length(W)
    % Randomly pick a few weights in the hidden layer and check gradient
    bias_rows = randperm(size(b{layer_idx}, 1), num_samples);

    num_failures = 0;
    for idx=1:num_samples

        i = bias_rows(idx);

        % Compute loss for bias - epsilon
        original_bias = b{layer_idx}(i);
        b{layer_idx}(i) = b{layer_idx}(i) - epsilon;
        [~, ~, ~] = Forward(W, b, data_vector');     
        [accuracy_minusepsilon, loss_minusepsilon] = ComputeAccuracyAndLoss(W, b, data_vector, label_vector);

        % Compute loss for weight + epsilon
        b{layer_idx}(i) = b{layer_idx}(i) + 2*epsilon;
        [output, act_h, act_a] = Forward(W, b, data_vector');     
        [accuracy_plusepsilon, loss_plusepsilon] = ComputeAccuracyAndLoss(W, b, data_vector, label_vector);

        % Validate gradient
        gradient_approx = (loss_plusepsilon - loss_minusepsilon)/(2*epsilon);
        gradient_backprop = grad_b{layer_idx}(i);

        if (abs(gradient_approx - gradient_backprop) > check_threshold)
            fprintf('Gradient check failed for bias index %.5f, %.5f, %10f, %10f\n', i, j, gradient_approx, gradient_backprop);
            num_failures = num_failures + 1;
        end

        % Reset weight.
        b{layer_idx}(i) = original_bias;
    end
    fprintf('Num failures for bias in layer %1d is %1d out of %1d samples\n', layer_idx, num_failures, num_samples);
end


