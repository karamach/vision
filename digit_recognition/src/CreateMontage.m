function [img] = CreateMontage(W, dim1, dim2)
   % W is of the form Num_nodes X Num_features
   montageCells = cell(dim1, dim2);
   count = 1;
   for i = 1:dim1
       for j = 1:dim2
          montageCells{i, j} = mat2gray(reshape(W(count, :), 28, 28));    
          count = count+1;
       end
   end    
   img = montage(cell2mat(montageCells))
end