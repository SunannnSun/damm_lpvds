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
data_name = "3D_Cshape_top.mat"
input_data = load_data(data_name)



# process and plot input data
Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)
plot_tools.plot_reference_trajectories_DS(Data, att, 100, 20)




dim, num = Data.shape

param_dict ={
    "mu_0":           np.zeros((dim, )), 
    "sigma_0":        0.5 * np.eye(dim),
    "nu_0":           dim,
    "kappa_0":        1,
    "sigma_dir_0":    0.1,
}

damm = damm_class(param_dict)         
damm.begin(Data)
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



data_name = "3D_Cshape_bottom.mat"
input_data = load_data(data_name)
Data_next, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)

plot_tools.plot_incremental(Data_next, Data)

damm.begin_next(Data_next)


Data = np.hstack((Data, Data_next))
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

 
 
# # process and plot input data
# Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)
# plot_tools.plot_reference_trajectories_DS(Data, att, 100, 20)


# concatenate data together and assignment label

# but the keep the original assignment labels and original data

# concatenate the data but also initialize the new assignment labels randomly

# using the original framework, the assignment labels are only intialized within the c++ code

# need to accomodate the fact that the new assignment labels need to be initialized wihile keeping the old ones intact




# the C++ source code has to take an additional arguments which is the assignment label of the entire data sets,
# which means that the built-in code in c++ that randomize the assignment labels needs to be deactivated


# DAMM used to take two arguments, the data itself and the paramenter_dictionary
# now it can take an additional arugment


# the goal is to keep the incremental learning separate from the DAMM module and make it only stand alone in the DAMM-lpvds 
# interface, hence isolating the functionality between modules.


# the previous assignment_label is always available in log/assignment.bin from the last run and will only overwritten until 
# another run; hence we can always the extract the assignmeny labels from the previous run in the interface and concatenate it
# with the newly intiailized randomly assginment labels for the new data


# the datawise, we however dont have a local copy, but the idea of incremental leanring is that the entire paradigm is run within
# one file, hence the local variables should be saved which include the data itself, the ultimate goal is to use a while loop to
# continuously incrementally add new data and assignment labels by running DAMM


# a good way to start is always try to open the assginemt.bin in the log folder, if such file does not exist, it means that this 
# is the first time running the function, and no old data exists, and we would like to keep this procedure in the interface



# if such assignment.bin file does not exist, it means that this is the first batch of data and damm needs to be run by not passing 
# the any assignmenty label, so the code would run as normally do