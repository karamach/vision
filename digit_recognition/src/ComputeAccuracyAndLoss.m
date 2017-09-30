function [accuracy, loss] = ComputeAccuracyAndLoss(W, b, data, labels, gamma, beta, use_bn, act_func)
% ComputeAccuracyAndLoss Compute accuracy and loss for the given data
% Input: W is the weights of a pre trained network
%        b is the bias of a pre trained network
%        data is the training, validation or test data
%        labels is the label for the input data
%        gamma is the batch normalization scale coefficient
%        beta is the batch normalization shift coefficient
%        use_bn is the flag for using batch normalization
%        act_func is the activation function to be used in hidden layer
% Output: Accuracy is the classification accuracy
%         Loss is the cross entropy loss
    outputs = Classify(W, b, data, gamma, beta, use_bn, act_func);
    data_size = size(data, 1);
    accuracy = 0;
    cross_entropy_loss = 0;
    for i=1:data_size
        [~, index] = max(outputs(i, :));
        accuracy = accuracy + labels(i, index);        
        cross_entropy_loss = cross_entropy_loss + log(labels(i, :) * outputs(i,:)');
    end
    accuracy = accuracy/data_size;
    loss = -1 * cross_entropy_loss/data_size;
end
