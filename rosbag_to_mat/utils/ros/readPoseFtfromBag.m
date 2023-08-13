function [ Pose, FT ] = readPoseFtfromBag(bag, pose_topic, ft_topic, varargin )
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here

% Functions for each topic type
% Functions for each topic type
if nargin == 2 
    position     = @(p) p.pose.position;
    orientation  = @(p) p.pose.orientation;   
else
    position     = @(pose) pose.position;
    orientation  = @(pose) pose.orientation;
end

force        = @(w) w.wrench.force;
    torque       = @(w) w.wrench.torque;   

% Rotation Converter from Quat to Euler
converter = @(x) (R2rpy(quaternion2matrix([x(4);x(1:3)]))');

% Read Pose Topics
[msgs, meta] = bag.readAll(pose_topic);
[pos] = ros.msgs2mat(msgs, position);

[msgs, meta] = bag.readAll(pose_topic);
[ori] = ros.msgs2mat(msgs, orientation); 
pose_t = cellfun(@(x) x.time.time, meta); % Time Stamps

Pose = [pos;ori(4,:);ori(1:3,:);pose_t];

% Read Force/Torque Topics
[msgs, meta] = bag.readAll(ft_topic);
[force] = ros.msgs2mat(msgs, force);

[msgs, meta] = bag.readAll(ft_topic);
[torque]   = ros.msgs2mat(msgs, torque); 
ft_t       = cellfun(@(x) x.time.time, meta); % Time Stamps

FT = [force;torque;ft_t];

end

