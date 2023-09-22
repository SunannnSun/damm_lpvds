import os
import numpy as np
import pyLasaDataset as lasa
from scipy.io    import loadmat, savemat

from damm.main   import damm   as damm_class
from ds_opt.main import ds_opt as dsopt_class
from util import load_tools, process_bag, plot_reference_trajectories_DS


dir_path     = os.path.dirname(os.path.realpath(__file__))
input_path   = os.path.join(dir_path, 'input.mat')
output_path  = os.path.join(dir_path, 'output.json')

'''
Option 1 PC-GMM benchmark data: 
    located in dataset/pc-gmm-data; must be renamed input.mat and placed under the root directory
Option 2 DAMM demo data: 
    located in dataset/pc-gmm-data; must be renamed input.mat and placed under the root directory
Option 3 LASA benchmark dataset:   
    need to specify the dataset by changing the name in data=lasa.DataSet.name 
'''

input_method = 3

if input_method == 1:
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
        # input_data = data_[:]

elif input_method == 2:
    input_data    = process_bag.process_bag_file(input_path)


elif input_method ==3:
    #[Angle, BendedLine, CShape, DoubleBendedLine, GShape, heee, JShape, JShape_2, Khamesh, Leaf_1]
    #[Leaf_2, Line, LShape, NShape, PShape, RShape, Saeghe, Sharpc, Sine, Snake]
    #[Spoon, Sshape, Trapezoid, Worm, WShape, Zshape, Multi_Models_1 Multi_Models_2, Multi_Models_3, Multi_Models_4]

    data = lasa.DataSet.Saeghe
    demos = data.demos 
    sub_sample = 3
    L = len(demos)
    input_data = np.empty((L, 1), dtype=object)
    for l in range(L):
        pos = demos[l].pos[:, ::sub_sample]
        vel = demos[l].vel[:, ::sub_sample]
        input_data[l, 0] = np.vstack((pos, vel))


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



damm = damm_class(Data)         
if damm.begin() == 0:
    damm.result(if_plot=True)



ds_opt = dsopt_class(data_dict, output_path)
ds_opt.begin()
ds_opt.evaluate()
ds_opt.make_plot()