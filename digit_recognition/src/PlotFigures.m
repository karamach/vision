function PlotFigures(num_epoch, params, train_loss_cum, validation_loss_cum, train_err_cum, validation_err_cum, loss_output_file, error_output_file)
    epochs = (1:num_epoch)';    

    % Plot loss
    f = figure();
    plot(epochs, cell2mat(train_loss_cum), 'r', epochs, cell2mat(validation_loss_cum), 'g') ;
    title('Loss vs Epoch');
    legend('Train Loss','Validation Loss');
    xlabel('Epoch');
    ylabel('Loss');
    dim = [0.4 0.6 0.3 0.3];
    annotation('textbox', dim, 'Color', 'blue', 'String', params,'FitBoxToText','on', 'LineStyle','-');
    saveas(f, loss_output_file)
    
    % plot error
    f = figure();
    plot(epochs, cell2mat(train_err_cum), 'r', epochs, cell2mat(validation_err_cum), 'g') ;
    title('Error vs Epoch');
    legend('Train Error','Validation Error');
    xlabel('Epoch');
    ylabel('Error');
    dim = [0.4 0.6 0.3 0.3];
    annotation('textbox', dim, 'Color', 'blue', 'String', params,'FitBoxToText','on', 'LineStyle','-');
    saveas(f, error_output_file)
end
