import os
import numpy as np
from scipy.io import loadmat



def load_dataset_DS(pkg_dir, dataset, sub_sample, nb_trajectories):
    dataset_name = []
    if dataset == 0:
        dataset_name = r'2D_messy-snake.mat'
    elif dataset == 1:
        dataset_name = r'2D_messy-snake.mat'
    elif dataset == 2:
        dataset_name = r'2D_Lshape.mat'
    elif dataset == 3:
        dataset_name = r'2D_Ashape.mat'
    elif dataset == 4:
        dataset_name = r'2D_Sshape.mat'
    elif dataset == 5:
        dataset_name = r'2D_multi-behavior.mat'
    elif dataset == 6:
        dataset_name = r'3D_viapoint_3.mat'
    elif dataset == 7:
        dataset_name = r'3D_sink.mat'
    elif dataset == 8:
        dataset_name = r'3D_Cshape_bottom.mat'
    elif dataset == 9:
        dataset_name = r'3D_Cshape_top.mat'
    elif dataset == 10:
        dataset_name = r'3D-pick-box.mat'
        nb_trajectories = 4
    elif dataset == 11:
        dataset_name = r'iCubHuman_demos.mat'
        nb_trajectories = 3
    elif dataset == 12:
        dataset_name = r'pnp_raw.mat'
        nb_trajectories = 3

    if not sub_sample:
        sub_sample = 2

    final_dir = os.path.join(pkg_dir,  'data', dataset_name)


    if dataset == 1:
        print("can not run in original matlab code, so this function we don't currently implement it")
        return None

    elif dataset <= 5:
        # 2022/09/10 检查出数据load错误
        data_ = loadmat(r"{}".format(final_dir))
        data_ = np.array(data_["data"])
        N = len(data_[0])
        data = data_.reshape((N, 1))
        Data, Data_sh, att, x0_all, dt, data, traj_length = processDataStructure(data)

    else:
        data_ = loadmat(r"{}".format(final_dir))
        data_ = np.array(data_["data"])
        N = len(data_)
        traj = np.random.choice(np.arange(N), nb_trajectories, replace=False)
        # traj = np.array([6, 8, 3, 5]) - 1
        data = data_[traj]
        for l in np.arange(nb_trajectories):
            # Gather Data
            if dataset == 11:
                print('this should be fixed later')
            else:
                data[l][0] = data[l][0][:, ::sub_sample]
        Data, Data_sh, att, x0_all, dt, data, traj_length = processDataStructure(data)

    return Data, Data_sh, att, x0_all, dt, data, traj_length





def processDataStructure(data):
    N = int(len(data))
    M = int(len(data[0][0]) / 2)
    att_ = data[0][0][0:M, -1].reshape(M, 1)
    for n in np.arange(1, N):
        att = data[n][0][0:M, -1].reshape(M, 1)
        att_ = np.concatenate((att_, att), axis=1)

    att = np.mean(att_, axis=1, keepdims=True)
    shifts = att_ - np.repeat(att, N, axis=1)
    Data = np.array([])
    x0_all = np.array([])
    Data_sh = np.array([])
    traj_length = []
    for l in np.arange(N):
        # Gather Data
        data_ = data[l][0].copy()
        traj_length.append(data_.shape[1])
        shifts_ = np.repeat(shifts[:, l].reshape(len(shifts), 1), len(data_[0]), axis=1)
        data_[0:M, :] = data_[0:M, :] - shifts_
        data_[M:, -1] = 0
        data_[M:, -2] = (data_[M:, -1] + np.zeros(M)) / 2
        data_[M:, -3] = (data_[M:, -3] + data_[M:, -2])/2
        # All starting position for reproduction accuracy comparison
        if l == 0:
            Data = data_.copy()
            x0_all = np.copy(data_[0:M, 0].reshape(M, 1))
        else:
            Data = np.concatenate((Data, data_), axis=1)
            x0_all = np.concatenate((x0_all, data_[0:M, 0].reshape(M, 1)), axis=1)
        # Shift data to origin for Sina's approach + SEDS
        data_[0:M, :] = data_[0:M, :] - np.repeat(att, len(data_[0]), axis = 1)
        data_[M:, -1] = 0
        if l == 0:
            Data_sh = data_
        else:
            Data_sh = np.concatenate((Data_sh, data_), axis=1)
        data[l][0] = data_

    data_12 = data[0][0][:, 0:M]
    dt = np.abs((data_12[0][0] - data_12[0][1]) / data_12[M][0])
    
    return Data, Data_sh, att, x0_all, dt, data, np.array(traj_length)