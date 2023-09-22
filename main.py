import os
import numpy as np
from scipy.io import loadmat
from scipy.io import savemat 
import pyLasaDataset as lasa




from damm.main   import damm   as damm_class
from ds_opt.main import ds_opt as dsopt_class
from util import load_tools, process_bag, plot_reference_trajectories_DS

 
# sys.path.append(os.path.join(dir_path, 'ds_opt_ood'))
# from ds_opt_ood.main import DsOpt as dsopt_class


'''
#############################################  Input method ###############################################
#### 1. PC-GMM benchmark dataset; must be named input.mat and placed under the same directory #############
#### 2. LASA benchmark dataset; need to specify the data by changing the name in data=lasa.DataSet.name ###
#### 3. DAMM demo data; must be named all.mat and placed under the same directory #########################
'''


input_method = 1
dir_path     = os.path.dirname(os.path.realpath(__file__))

if input_method == 1:
    input_path    = os.path.join(dir_path, 'input.mat')
    output_path   = os.path.join(dir_path, 'output.json')

    dim = 2
    # # Load Data
    if dim ==2:
        data_ = loadmat(r"{}".format(input_path))
        data_ = np.array(data_["data"])
        N = len(data_[0])
        input_data = data_.reshape((N, 1))
    elif dim == 3:
        N = len(data_)
        # traj = np.random.choice(np.arange(N), 4, replace=False)
        traj = np.array([6, 8, 3, 5]) - 1
        input_data = data_[traj]


elif input_method ==3:
    #[Angle, BendedLine, CShape, DoubleBendedLine, GShape, heee, JShape, JShape_2, Khamesh, Leaf_1]
    #[Leaf_2, Line, LShape, NShape, PShape, RShape, Saeghe, Sharpc, Sine, Snake]
    #[Spoon, Sshape, Trapezoid, Worm, WShape, Zshape, Multi_Models_1 Multi_Models_2, Multi_Models_3, Multi_Models_4]

    sub_sample = 3
    data = lasa.DataSet.Snake
    demos = data.demos 
    sub_sample = 3
    L = len(demos)
    input_data = np.empty((L, 1), dtype=object)
    for l in range(L):
        pos = demos[l].pos[:, ::sub_sample]
        vel = demos[l].vel[:, ::sub_sample]
        input_data[l, 0] = np.vstack((pos, vel))

elif input_method == 3:
    input_path    = os.path.join(dir_path, 'all.mat')
    input_data = process_bag.process_bag_file(input_path)


Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)
plot_reference_trajectories_DS.plot_reference_trajectories_DS(Data, att, 100, 20)


data_dict = {
    "Data": Data,
    "Data_sh": Data_sh,
    "att": np.array(att),
    "x0_all": x0_all,
    "dt": dt,
    "traj_length":traj_length
}


"""
# # Run ds_opt and output JSON
ds_opt = dsopt_class(data_dict, os.path.join(dir_path, "output.json"))
ds_opt.begin()
ds_opt.evaluate()
ds_opt.make_plot()