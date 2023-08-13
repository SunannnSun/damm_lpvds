function [ Velocity ] = readTwistfromBag(bag, twist_topic)
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here

% Functions for each topic type
linear     = @(twist) twist.linear;
angular    = @(twist) twist.angular;

% Read Pose Topics
[msgs, meta]  = bag.readAll(twist_topic);
[vel_linear]  = ros.msgs2mat(msgs, linear);
[vel_angular] = ros.msgs2mat(msgs, angular);
vel_t = cellfun(@(x) x.time.time, meta); % Time Stamps

Velocity = [vel_linear;vel_angular;vel_t];

end

