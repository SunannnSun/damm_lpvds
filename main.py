import os
import numpy as np

from damm.main   import damm   as damm_class
from ds_opt.main import ds_opt as dsopt_class
from util import load_tools, plot_tools, process_bag



# load .mat file using process_bag function
dir_path     = os.path.dirname(os.path.realpath(__file__))
input_path    = os.path.join(dir_path, 'input.mat')
input_data    = process_bag.process_bag_file(input_path)


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