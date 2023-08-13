function [data] = extractPoseStamped(bag, topic_name)

% Select Topic from bag
bSel = select(bag, 'Topic', topic_name);    
msgStructs = readMessages(bSel,'DataFormat','struct');

% Extract Position Trajectories 
Positions = [cellfun(@(m) double(m.Pose.Position.X),msgStructs)';      
            cellfun(@(m) double(m.Pose.Position.Y),msgStructs)';
            cellfun(@(m) double(m.Pose.Position.Z),msgStructs)'];
% Extract Orientation Trajectories
Orientations = [cellfun(@(m) double(m.Pose.Orientation.X),msgStructs)';     
               cellfun(@(m) double(m.Pose.Orientation.Y),msgStructs)';
               cellfun(@(m) double(m.Pose.Orientation.Z),msgStructs)';
               cellfun(@(m) double(m.Pose.Orientation.W),msgStructs)'];

% Extract Timestamp Trajectories
Timestamps   = cellfun(@(m) double(m.Header.Stamp.Sec), msgStructs)' + (10^-9)*cellfun(@(m) double(m.Header.Stamp.Nsec), msgStructs)';
Timestamps   = Timestamps - Timestamps(1); 

% Construct Data Struct
data.pose     = [Positions; Orientations; Timestamps];
data.dt       = mean(diff(Timestamps));
data.origin   = msgStructs{1}.Header.FrameId;

end

