import os, subprocess
import numpy as np
from scipy.io import loadmat

from damm.main   import damm   as damm_class
from ds_opt.main import ds_opt as dsopt_class
from util import load_tools, plot_tools, process_bag
import matlab.engine

import time
from time import perf_counter



if __name__ == "__main__":
    
    # define path
    dir_path      = os.path.dirname(os.path.realpath(__file__))
    input_path    = os.path.join(dir_path,'log', 'mat', 'all.mat')
    output_path   = os.path.join(dir_path, 'output.json')

    mat_path      = os.path.join(dir_path,'log', 'mat')
    rosbag_path   = os.path.join(dir_path,'log', 'ros_bag')
    archive_path  = os.path.join(dir_path,'log', 'archive')
    model_path    = os.path.join(dir_path, '..', '..', 'franka_ws', 'src', 'lfd_ds', 'model', 'damm1')

    
    # initialize a damm class with hyperparameters
    dim = 6
    param_dict ={
    "mu_0":           np.zeros((dim, )), 
    "sigma_0":        0.5 * np.eye(dim),
    "nu_0":           dim,
    "kappa_0":        0.1,
    "sigma_dir_0":    0.05,
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
        if i == 0:
            Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)
        else:
            Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data, att)
        # att[1]  = att[1]  + 0.05 
        # if i==1:
        #     att[-1] = att[-1] + 0.03
        # if i==0:
        #     att[-1] =att[-1] - 0.1

        if i==0:
            plot_tools.plot_reference_trajectories_DS(Data, att, 100, 20)
        else:
            plot_tools.plot_incremental(Data, prev_Data)
        
        if i==0:
            damm.begin(Data)
        else:
            damm.begin_next(Data)
        damm.evaluate(x0_all)
        damm.plot()

        if i!=0:
            Data = np.hstack((prev_Data, Data))


        # run ds-opt
        data_dict = {
            "Data": Data,
            "Data_sh": Data_sh,
            "att": np.array(att),
            "x0_all": x0_all,
            "dt": dt,
            "traj_length":traj_length
        }

        t0 = time.time()
        T0 = perf_counter() 

        ds_opt = dsopt_class(data_dict, output_path) 
        ds_opt.begin()
        t1 = time.time()
        T1 = perf_counter() 
        
        ds_opt.evaluate()
        # print("Time to Finish Optimization: ", t1-t0)
        # print("Time to Finish Optimization: ", T1-T0)
        ds_opt.plot()



        allfiles = os.listdir(mat_path)
        for f in allfiles:
            src_path = os.path.join(mat_path, f)
            dst_path = os.path.join(archive_path, f)
            os.rename(src_path, dst_path)


        allfiles = os.listdir(rosbag_path)
        for f in allfiles:
            src_path = os.path.join(rosbag_path, f)
            dst_path = os.path.join(archive_path, f)
            os.rename(src_path, dst_path)

        i+=1

        prev_Data = Data

        os.rename(os.path.join(dir_path, "output.json"), os.path.join(model_path, '0.json'))

    eng.quit()



