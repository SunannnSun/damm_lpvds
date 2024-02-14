import os
import numpy as np
import matplotlib.pyplot as plt

# Relative Import
from .util import load_tools
from .damm.main import damm as damm_class
from .ds_opt.main import ds_opt as dsopt_class
from .ds_opt.util.math_tools import gaussian_tools



class damm_lpvds():
    def __init__(self, Data, Data_sh, att, x0_all, dt, traj_length, output_path) -> None:

        self.data = {
            "Data": Data,
            "Data_sh": Data_sh,
            "att": np.array(att),
            "x0_all": x0_all,
            "dt": dt,
            "traj_length":traj_length
        }


        dim = Data.shape[0]


        self.param ={
            "mu_0":           np.zeros((dim, )), 
            "sigma_0":        1 * np.eye(dim),
            "nu_0":           dim,
            "kappa_0":        0,
            "sigma_dir_0":    0.1,
            "min_threshold":  10
        }

        self.output_path = output_path



    def _cluster(self):
        damm = damm_class(self.param)      
        self.Priors, self.Mu, self.Sigma =  damm.begin(self.data["Data"])
        self.K = damm.K

        damm.plot()
        # damm.logOut()



    def _optimize(self):

        ds_opt = dsopt_class(self.data, self.Priors, self.Mu, self.Sigma)
        self.A, self.b = ds_opt.begin()

        # ds_opt.plot()

        # ds_opt.evaluate()
        # ds_opt.logOut()

        self.ds_opt = ds_opt


    def begin(self):
        self._cluster()
        self._optimize()



    def step(self, x, dt):
 
        x_next = self.ds_opt.step(x, dt)

        return x_next





if __name__ == "__main__":

    # choose input option
    input_message = '''
    Please choose a data input option:
    1. PC-GMM benchmark data
    2. LASA benchmark data
    3. DAMM demo data
    Enter the corresponding option number: '''


    input_opt = input(input_message)


    input_data = load_tools.load_data(int(input_opt))
    Data, Data_sh, att, x0_all, dt, _, traj_length = load_tools.processDataStructure(input_data)
    # plot_tools.plot_reference_trajectories_DS(Data, att, 100, 20)

    output_path  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output.json')
    # # output_path  = 'output.json'

    damm_lpvds = damm_lpvds(Data, Data_sh, att, x0_all, dt, traj_length, output_path)

    damm_lpvds.begin()

    plt.show()