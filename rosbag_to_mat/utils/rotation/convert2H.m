function [ H ] = convert2H( X )
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here

H = zeros(4,4,size(X,2));
H(1:4,1:4,1:end) = repmat(eye(4),[1 1 size(X,2)]);
H(1:3,1:3,1:end) = reshape(quaternion_my(X(4:7,1:end)),[3 3 size(X,2)]);
H(1:3,4,1:end) = reshape(X(1:3,1:end),[3 1 size(X,2)]);   

end

