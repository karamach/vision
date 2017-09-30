load('output/model.mat');

% load test data
test_data = textread('../data/digitstest.txt','','delimiter',',');
test_features = test_data(:, 1:num_features);
test_labels = test_data(:, num_features+1)' + 1; % convert to 1 to 10 for 1 based indexing for ind2vec
test_labels = full(ind2vec(test_labels)');

[test_acc, test_loss] = ComputeAccuracyAndLoss(W, b, test_features, test_labels,  gamma, beta, use_bn, act_func);

fprintf('Testing Loss %f, train_acc: %.5f, validation_err: %.5f, train_loss: %.5f, validation_loss: %.5f\n',  test_acc, test_loss);

