import os, sys
import numpy as np
from scipy.io import loadmat



def load_data(input_opt):

    if input_opt == 1:
        print("\nYou selected PC-GMM benchmark data.\n")
        pcgmm_list = ["3D_sink", "3D_viapoint_1", "3D-cube-pick", "3D_viapoint_2", "2D_Lshape",  "2D_incremental_1", "2D_multi-behavior", "2D_messy-snake"]
        
        message = """Available Models: \n"""
        for i in range(len(pcgmm_list)):
            message += "{:2}) {: <18} ".format(i+1, pcgmm_list[i])
            if (i+1) % 6 ==0:
                message += "\n"
        message += '\nEnter the corresponding option number [type 0 to exit]: '
        
        data_opt = int(input(message))

        if data_opt == 0:
            sys.exit()
        elif data_opt<0 or data_opt > len(pcgmm_list):
            print("Invalid data option")
            sys.exit()
    
        data_name = str(pcgmm_list[data_opt-1]) + ".mat"
        input_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..", "dataset", "pc-gmm-data", data_name)

        data_ = loadmat(r"{}".format(input_path))
        data_ = np.array(data_["data"])
        dim = data_[0][0].shape[0]/2
        if dim == 2:
            N = len(data_[0])
            input_data = data_.reshape((N, 1))
        elif dim == 3:
            N = len(data_)
            traj = np.random.choice(np.arange(N), 6, replace=False)
            # traj = np.array([6, 8, 3, 5]) - 1
            input_data = data_[traj]  
            # input_data = data_[:]


    elif input_opt == 2:
        print("\nYou selected LASA benchmark dataset.\n")

        # suppress print message from lasa package
        original_stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')
        import pyLasaDataset as lasa
        sys.stdout = original_stdout

        lasa_list = ["Angle", "BendedLine", "CShape", "DoubleBendedLine", "GShape", "heee", "JShape", "JShape_2", "Khamesh", "Leaf_1",
        "Leaf_2", "Line", "LShape", "NShape", "PShape", "RShape", "Saeghe", "Sharpc", "Sine", "Snake",
        "Spoon", "Sshape", "Trapezoid", "Worm", "WShape", "Zshape", "Multi_Models_1", "Multi_Models_2", "Multi_Models_3", "Multi_Models_4"]

        message = """Available Models: \n"""
        for i in range(len(lasa_list)):
            message += "{:2}) {: <18} ".format(i+1, lasa_list[i])
            if (i+1) % 6 ==0:
                message += "\n"
        message += '\nEnter the corresponding option number [type 0 to exit]: '
        
        data_opt = int(input(message))

        if data_opt == 0:
            sys.exit()
        elif data_opt<0 or data_opt > len(lasa_list):
            print("Invalid data option")
            sys.exit()

        data = getattr(lasa.DataSet, lasa_list[data_opt-1])
        demos = data.demos 

        sub_sample = 1
        L = len(demos)
        input_data = np.empty((L, 1), dtype=object)
        for l in range(L):
            pos = demos[l].pos[:, ::sub_sample]
            vel = demos[l].vel[:, ::sub_sample]
            input_data[l, 0] = np.vstack((pos, vel))


    elif input_opt == 3:
        print("\nYou selected DAMM demo dataset.\n")

        from . import process_bag
        damm_list = ["bridge", "Nshape"]
        
        message = """Available Models: \n"""
        for i in range(len(damm_list)):
            message += "{:2}) {: <18} ".format(i+1, damm_list[i])
            if (i+1) % 6 ==0:
                message += "\n"
        message += '\nEnter the corresponding option number [type 0 to exit]: '
        
        data_opt = int(input(message))
    
        folder_name = str(damm_list[data_opt-1])
        input_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..", "dataset", "damm-demo-data", folder_name, "all.mat")
        input_data    = process_bag.process_bag_file(input_path)

    return input_data






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