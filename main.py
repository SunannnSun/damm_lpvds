import os
import numpy as np
from scipy.io    import loadmat, savemat

from damm.main   import damm   as damm_class
from ds_opt.main import ds_opt as dsopt_class
from util import load_tools, plot_tools, process_bag


dir_path     = os.path.dirname(os.path.realpath(__file__))
input_path   = os.path.join(dir_path, 'input.mat')
output_path  = os.path.join(dir_path, 'output.json')


input_message = '''
Please choose a data input option:
1. PC-GMM benchmark data
2. LASA benchmark data
3. DAMM demo data
Enter the corresponding option number: '''

input_opt = input(input_message)


input_data = load_tools.load_data(int(input_opt))
Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)
plot_tools.plot_reference_trajectories_DS(Data, att, 100, 20)


data_dict = {
    "Data": Data,
    "Data_sh": Data_sh,
    "att": np.array(att),
    "x0_all": x0_all,
    "dt": dt,
    "traj_length":traj_length
}

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


ds_opt = dsopt_class(data_dict, output_path)
ds_opt.begin()
ds_opt.evaluate()
ds_opt.plot()