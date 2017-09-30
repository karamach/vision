% Initialize params
num_epoch = 200;
classes = 10;
num_features = 784;
num_hidden_nodes = 100;
num_hidden_layers = 1;
layers = [num_features, repmat(num_hidden_nodes, 1, num_hidden_layers), classes];
batch_size = 32;
learning_rate = 0.1;
momentum = 0.8;
reg_coeff = 0.001;
use_bn = 1;
act_func = 'sig';
params = {strcat('numEpoch=', string(num_epoch)), strcat('numFeatures=', string(num_features)), strcat('classes=', string(classes)),strcat('numHiddenLayers=', string(num_hidden_layers)), strcat('numHiddenNodes=', string(num_hidden_nodes)), strcat('batchSz=', string(batch_size)), strcat('lr=', string(learning_rate)), strcat('momentum=', string(momentum)), strcat('regCoeff=', string(reg_coeff)), strcat('useBN=', string(use_bn)), strcat('actFunc=', string(act_func))};

% load train data
train_data = textread('../data/digitstrain.txt','','delimiter',',');
train_features = train_data(:, 1:num_features);
train_labels = train_data(:, num_features+1)' + 1; % convert to 1 to 10 for 1 based indexing for ind2vec
train_labels = full(ind2vec(train_labels)');

% load validation data
validation_data = textread('../data/digitsvalid.txt','','delimiter',',');
validation_features = validation_data(:, 1:num_features);
validation_labels = validation_data(:, num_features+1)' + 1; % convert to 1 to 10 for 1 based indexing for ind2vec
validation_labels = full(ind2vec(validation_labels)');

% SGD
char(cellstr(params))
[train_err_cum, train_loss_cum, validation_err_cum, validation_loss_cum] = SGD(num_epoch, layers, train_features, train_labels, validation_features, validation_labels,  batch_size, learning_rate, momentum, reg_coeff, use_bn, act_func, 'output/model.mat');

% Plot loss and error
PlotFigures(num_epoch, params, train_loss_cum, validation_loss_cum, train_err_cum, validation_err_cum, 'output/loss_vs_epoch.png', 'output/error_vs_epoch.png');


