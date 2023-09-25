import os, subprocess
import numpy as np
from scipy.io import loadmat



from damm.main   import damm   as damm_class
from ds_opt.main import ds_opt as dsopt_class
from util import load_tools, plot_tools, process_bag

def load_data(data_name):
    input_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dataset", "pc-gmm-data", data_name)

    data_ = loadmat(r"{}".format(input_path))
    data_ = np.array(data_["data"])
    dim = data_[0][0].shape[0]/2
    if dim == 2:
        N = len(data_[0])
        input_data = data_.reshape((N, 1))
    elif dim == 3:
        N = len(data_)
        # traj = np.random.choice(np.arange(N), 4, replace=False)
        traj = np.array([6, 8, 3, 5]) - 1
        input_data = data_[traj]  
    return input_data
    


# load .mat file using process_bag function

data_name = "3D_Cshape_bottom.mat"
input_data = load_data(data_name)



# process and plot input data
Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)
plot_tools.plot_reference_trajectories_DS(Data, att, 100, 20)


# damm clustering
dim = Data.shape[0]

param_dict ={
    "mu_0":           np.zeros((dim, )), 
    "sigma_0":        0.5 * np.eye(dim),
    "nu_0":           dim,
    "kappa_0":        1,
    "sigma_dir_0":    0.1,
}

damm = damm_class(Data, param_dict)         
damm.begin()
damm.evaluate()
damm.plot()


# ds optimization 
data_dict = {
    "Data": Data,
    "Data_sh": Data_sh,
    "att": np.array(att),
    "x0_all": x0_all,
    "dt": dt,
    "traj_length":traj_length
}

output_path  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output.json')

ds_opt = dsopt_class(data_dict, output_path)
ds_opt.begin()
ds_opt.evaluate()
ds_opt.plot()



second_path    = os.path.join(dir_path, '3D_Cshape_top.mat')
second_data    = process_bag.process_bag_file(second_path)
