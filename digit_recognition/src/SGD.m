function [train_err_cum, train_loss_cum, validation_err_cum, validation_loss_cum] = SGD(num_epoch, layers, train_features, train_labels, validation_features, validation_labels, batch_size, learning_rate, momentum, reg_coeff, use_bn, act_func, model_path)

    % Initialize network
    [W, b] = NormalizedInitialization(layers);
    [gamma, beta] = BNInitialization(layers);

    % Initialize variables
    train_acc_cum = cell(num_epoch, 1);
    train_err_cum = cell(num_epoch, 1);
    train_loss_cum = cell(num_epoch, 1);
    validation_acc_cum = cell(num_epoch, 1);
    validation_err_cum = cell(num_epoch, 1);
    validation_loss_cum = cell(num_epoch, 1);

    best_loss = intmax;
    
    % Train for num_epoch. Compute training and validation accuracy and loss
    for j = 1:num_epoch
        [W, b, gamma, beta] = TrainEpoch(W, b, train_features, train_labels, batch_size, learning_rate, momentum, reg_coeff, gamma, beta, use_bn, act_func);

        [train_acc, train_loss] = ComputeAccuracyAndLoss(W, b, train_features, train_labels,  gamma, beta, use_bn, act_func);
        [validation_acc, validation_loss] = ComputeAccuracyAndLoss(W, b, validation_features, validation_labels,  gamma, beta, use_bn, act_func);

        train_acc_cum{j} = train_acc; 
        train_err_cum{j} = 1-train_acc; 
        train_loss_cum{j} = train_loss;
        validation_acc_cum{j} = validation_acc;
        validation_err_cum{j} = 1-validation_acc;
        validation_loss_cum{j} = validation_loss;

        if (validation_loss < best_loss)
            save(model_path, 'W', 'b', 'gamma', 'beta', 'use_bn', 'act_func', 'num_epoch', 'layers', 'batch_size', 'learning_rate', 'momentum', 'reg_coeff');
            best_loss = validation_loss;
        end
        fprintf('Epoch %d, train_err: %.5f, validation_err: %.5f, train_loss: %.5f, validation_loss: %.5f\n', j, 1-train_acc, 1-validation_acc, train_loss, validation_loss)
    end        
end
 

