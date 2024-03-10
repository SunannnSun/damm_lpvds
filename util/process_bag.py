import numpy as np
import os, sys
from scipy.io import loadmat
from scipy.spatial.transform import Rotation as R



def process_bag_file(path):
    """
    Process .mat files converted from .bag files
    """

    data_ = loadmat(r"{}".format(path))

    data_ = data_['data_ee_pose']
    L = data_.shape[1]

    output_traj = np.empty((L, 1), dtype=object)
    index_list = []
    q_in = []


    sample_step =5
    vel_thresh = 1e-3 
    
    for l in range(L):
        data_l = data_[0, l]['pose'][0,0]
        pos_traj  = data_l[:3, ::sample_step]
        quat_traj = data_l[3:7, ::sample_step]
        time_traj = data_l[-1, ::sample_step].reshape(1,-1)

        raw_diff_pos = np.diff(pos_traj)
        vel_mag = np.linalg.norm(raw_diff_pos, axis=0).flatten()
        first_non_zero_index = np.argmax(vel_mag > vel_thresh)
        last_non_zero_index = len(vel_mag) - 1 - np.argmax(vel_mag[::-1] > vel_thresh)

        if first_non_zero_index >= last_non_zero_index:
            raise Exception("Sorry, vel are all zero")

        pos_traj  = pos_traj[:, first_non_zero_index:last_non_zero_index]
        quat_traj = quat_traj[:, first_non_zero_index:last_non_zero_index]
        time_traj = time_traj[:, first_non_zero_index:last_non_zero_index]

        pos_diff_traj  = np.diff(pos_traj)
        time_diff_traj = np.diff(time_traj)

        vel_traj = pos_diff_traj / time_diff_traj
        
        output_traj[l, 0] = np.vstack((pos_traj[:, 0:-1], vel_traj))

        q_ref = quat_traj[:, 0]
        for i in np.arange(1, quat_traj.shape[1]):
            if np.linalg.norm(q_ref - quat_traj[:, i]) > 1.5:
                quat_traj[:, i] *= -1
                q_ref = quat_traj[:, i]


        q_in_l = [R.from_quat(quat_traj[:, i]) for i in range(quat_traj.shape[1])]
        q_in  += q_in_l


        if l == 0:
            index_list.append(np.arange(0, len(q_in_l)))
        else:
            index_list.append(np.arange(index_list[-1][-1],  index_list[-1][-1] + len(q_in_l))+1)


    # quat_traj = [R.from_quat(quat_traj[:, i]) for i in range(quat_traj.shape[1])]

    return output_traj, q_in, index_list



if __name__ == '__main__':

    dir_path     = os.path.dirname(os.path.realpath(__file__))
    input_path    = os.path.join(dir_path, 'all.mat')

    output_traj = process_bag_file(input_path)

    print(output_traj.shape)