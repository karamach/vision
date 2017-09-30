train_data = textread('../data/digitstrain.txt','','delimiter',',');
train_features = train_data(:, 1:num_features);

num_instances_per_class = 300;
images = cell(10, 1);
for i=1:num_instances_per_class:3000    
    img = reshape(train_features(i,:), 28, 28)';
    filename = sprintf('../data/visualization/%d.png', round(i/num_instances_per_class));
    images{round(i/num_instances_per_class)+1} = reshape(img, 1, 784);
    imwrite(img, filename);
end

montage_img = get(CreateMontage(cell2mat(images), 1, 10), 'CData'); 
imwrite(montage_img, '../data/visualization/montage_1_10.png');