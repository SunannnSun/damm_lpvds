import sys, os
import numpy as np
from scipy.io import loadmat
from scipy.io import savemat 
from process_bag import process_bag_file
import pyLasaDataset as lasa

dir_path     = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.join(dir_path, 'damm'))
sys.path.append(os.path.join(dir_path, 'ds_opt_ood'))


from damm.damm import damm as damm_class
from ds_opt_ood.utils_ds import load_tools
# from ds_opt_ood.main import DsOpt
from ds_opt_ood.utils_ds.plotting_tool.plot_reference_trajectories_DS import plot_reference_trajectories_DS
 
# Temporary input method: 
# 1. loading PC-GMM benchmark dataset; must be named input.mat and placed under the same directory
# 2. loading LASA benchmark dataset; need to specify the data by changing the name in data=lasa.DataSet.name
# 3. loading real trajectory collected during rebuttal, must be named all.mat and placed under the same directory

input_method = 3

if input_method == 1:
    # Define Path
    input_path    = os.path.join(dir_path, 'input.mat')
    output_path   = os.path.join(dir_path, 'output.json')

    dim = 2
    # # Load Data
    if dim ==2:
        data_ = loadmat(r"{}".format(input_path))
        data_ = np.array(data_["data"])
        N = len(data_[0])
        input_data = data_.reshape((N, 1))
    # else:
    #     data_ = loadmat(r"{}".format(input_path))
    #     data_ = np.array(data_["data"])
    #     N = len(data_)
    #     # traj = np.random.choice(np.arange(N), 4, replace=False)
    #     traj = np.array([6, 8, 3, 5]) - 1
    #     input_data =


elif input_method ==2:
    #[Angle, BendedLine, CShape, DoubleBendedLine, GShape, heee, JShape, JShape_2, Khamesh, Leaf_1]
    #[Leaf_2, Line, LShape, NShape, PShape, RShape, Saeghe, Sharpc, Sine, Snake]
    #[Spoon, Sshape, Trapezoid, Worm, WShape, Zshape, Multi_Models_1 Multi_Models_2, Multi_Models_3, Multi_Models_4]

    sub_sample = 3
    data = lasa.DataSet.Snake
    demos = data.demos 

    L = len(demos)
    input_data = np.empty((L, 1), dtype=object)
    for l in range(L):
        pos = demos[l].pos[:, ::sub_sample]
        vel = demos[l].vel[:, ::sub_sample]
        input_data[l, 0] = np.vstack((pos, vel))

elif input_method == 3:

    input_path    = os.path.join(dir_path, 'all.mat')
    input_data = process_bag_file(input_path)
    input_data_copy = input_data.copy()


Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)


# att = np.array(att).reshape(3, 1)
# plot_reference_trajectories_DS(Data, att, 100, 20)

# print(Data.shape)
# import matplotlib.pyplot as plt

# plt.figure()
# ax = plt.axes(projection='3d')
# ax.scatter(Data[0, :], Data[1, :], Data[2, :], c='k', s=5)


# plt.show()
data_dict = {
    "Data": Data,
    "Data_sh": Data_sh,
    "att": att,
    "x0_all": x0_all,
    "dt": dt,
    "traj_length":traj_length
}


# # Run DAMM
DAMM = damm_class(Data)         
if DAMM.begin() == 0:
    DAMM.result(if_plot=True)

# Priors = DAMM.Priors
# Mu = DAMM.Mu
# Sigma = DAMM.Sigma


"""
# # Run ds_opt and output JSON
ds_opt = DsOpt(data_dict, os.path.join(dir_path, "output.json"))
ds_opt.begin()
ds_opt.evaluate()
ds_opt.make_plot()






# damm_output = {
#     'cov': Sigma,
#     'mu': Mu,
#     'pi': Priors,
#     'traj': input_data_copy
# }
# savemat('damm_output.mat', damm_output)

"""

