import os, subprocess
import numpy as np
from scipy.io import loadmat

from damm.main   import damm   as damm_class
from ds_opt.main import ds_opt as dsopt_class
from util import load_tools, plot_tools, process_bag
import matlab.engine


if __name__ == "__main__":
    
    # define path
    dir_path      = os.path.dirname(os.path.realpath(__file__))
    input_path    = os.path.join(dir_path,'log', 'mat', 'all.mat')
    output_path   = os.path.join(dir_path, 'output.json')

    
    # initialize a damm class with hyperparameters
    dim = 6
    param_dict ={
    "mu_0":           np.zeros((dim, )), 
    "sigma_0":        0.5 * np.eye(dim),
    "nu_0":           dim,
    "kappa_0":        1,
    "sigma_dir_0":    0.1,
    }
    damm = damm_class(param_dict)    


    # run matlab engine
    eng = matlab.engine.start_matlab()
    eng.cd(r'rosbag_to_mat')
    

    # incremental learning
    i = 0
    while True:
        message = 'Press enter to continue: '
        message_input = input(message)

        if message_input == 0:
            break

        # convert .rosbag to .mat 
        eng.process_rosbags(nargout=0)

        # read .mat file 
        input_data    = process_bag.process_bag_file(input_path)

        # process the raw data and run damm
        Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)
        plot_tools.plot_reference_trajectories_DS(Data, att, 100, 20)
        if i==0:
            damm.begin(Data)
        else:
            damm.begin_next(Data)
        
        # run ds-opt
        data_dict = {
            "Data": Data,
            "Data_sh": Data_sh,
            "att": np.array(att),
            "x0_all": x0_all,
            "dt": dt,
            "traj_length":traj_length
        }


        ds_opt = dsopt_class(data_dict, output_path) 
        ds_opt.begin()
        ds_opt.evaluate()
        ds_opt.plot()

        
    eng.quit()



