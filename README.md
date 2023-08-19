# damm_lpvds
This is the integrated interface of the Directionality-aware Mixture Model (DAMM) based Linear Parameter Varying Dynamical Systems (LPV-DS) framework. This package provides necessary tools to load data from different sources, and an environment to output the learned Dynamical System (DS) for real robot usage, using DAMM and optimization. Note this module does not consist of DAMM nor optimization package. Please follow the instruction below:


## Usage
Download modules
```
git clone https://github.com/SunannnSun/damm_lpvds.git
cd damm_lpvds
git clone https://github.com/SunannnSun/damm.git
git clone https://github.com/HuiTakami/ds_opt_ood.git
```

Compile damm module
- Please refer to the **compilation** section in [damm repository](https://github.com/SunannnSun/damm).

Create a python virtual environment and install the dependencies.
- Make sure to replace `/path/to/python3.8` with the correct path to the Python 3.8 executable on your system. 

```
virtualenv -p /path/to/python3.8 env3.8
source env3.8/bin/activate
pip install -r requirements.txt
```

Choose the input method in ```main.py``` and run command

```
python main.py
```