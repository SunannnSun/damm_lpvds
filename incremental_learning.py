import os, subprocess
import numpy as np
from scipy.io import loadmat

from damm.main   import damm   as damm_class
from ds_opt.main import ds_opt as dsopt_class
from util import load_tools, plot_tools, process_bag
import matlab.engine


if __name__ == "__main__":
    
    dir_path      = os.path.dirname(os.path.realpath(__file__))
    input_path    = os.path.join(dir_path,'log', 'mat', 'all.mat')


    # run matlab engine
    eng = matlab.engine.start_matlab()
    eng.cd(r'rosbag_to_mat')
    
    for i in range(5):
        message = 'Press enter to continue: '
        eng.process_rosbags(nargout=0)
        input_data    = process_bag.process_bag_file(input_path)
        Data_next, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)

        input(message)
        # damm.begin_next(Data_next)

        # concatenate new and old data and store as the old data

    eng.quit()



