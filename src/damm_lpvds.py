
import os
import numpy as np
import matplotlib.pyplot as plt

# Relative Import
from .util import load_tools, plot_tools
from .damm.main import damm as damm_class
from .ds_opt.main import ds_opt as dsopt_class
from .ds_opt.util.math_tools import gaussian_tools


class damm_lpvds():
    def __init__(self, Data, Data_sh, att, x0_all, dt, traj_length) -> None:

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
        
        file_path           = os.path.dirname(os.path.realpath(__file__))  
        self.output_path    = os.path.join(os.path.dirname(file_path), 'output_pos.json')
        # self.output_path = output_path



    def _cluster(self):
        damm = damm_class(self.param)      
        self.Priors, self.Mu, self.Sigma =  damm.begin(self.data["Data"])
        self.K = damm.K

        damm.plot()
        damm.logOut(self.output_path)



    def _optimize(self):

        ds_opt = dsopt_class(self.data, self.Priors, self.Mu, self.Sigma)
        self.A, self.b = ds_opt.begin()

        ds_opt.plot()

        ds_opt.evaluate()
        ds_opt.logOut(self.output_path)

        self.ds_opt = ds_opt


    def begin(self):
        self._cluster()
        self._optimize()



    def step(self, x, dt):
 
        x_next = self.ds_opt.step(x, dt)

        return x_next

