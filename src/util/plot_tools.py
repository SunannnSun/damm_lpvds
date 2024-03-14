import matplotlib.pyplot as plt
import numpy as np


def plot_reference_trajectories_DS(Data, att, vel_sample, vel_size):
    fig = plt.figure(figsize=(8, 6))
    M = len(Data) / 2  # store 1 Dim of Data
    if M == 2:
        ax = fig.add_subplot(111)
        ax.set_xlabel(r'$\xi_1$')
        ax.set_ylabel(r'$\xi_2$')
        ax.set_title('Reference Trajectory')

        # Plot the position trajectories
        plt.plot(Data[0], Data[1], 'ro', markersize=1)
        # plot attractor
        # plt.scatter(att[0], att[1], s=100, c='blue', alpha=0.5)
        plt.scatter(att[0], att[1], marker=(8, 2, 0), s=100, c='k')

        # Plot Velocities of Reference Trajectories
        vel_points = Data[:, ::vel_sample]
        U = np.zeros(len(vel_points[0]))
        V = np.zeros(len(vel_points[0]))  # （385,)
        for i in np.arange(0, len(vel_points[0])):
            dir_ = vel_points[2:, i] / np.linalg.norm(vel_points[2:, i])
            U[i] = dir_[0]
            V[i] = dir_[1]
        q = ax.quiver(vel_points[0], vel_points[1], U, V, width=0.005, scale=vel_size)
    else:
        ax = fig.add_subplot(projection='3d')
        ax.plot(Data[0], Data[1], Data[2], 'ro', markersize=1.5)
        ax.scatter(att[0], att[1], att[2], s=200, c='blue', alpha=0.5)
        ax.axis('auto')
        ax.set_title('Reference Trajectory')
        ax.set_xlabel(r'$\xi_1(m)$')
        ax.set_ylabel(r'$\xi_2(m)$')
        ax.set_zlabel(r'$\xi_3(m)$')
        vel_points = Data[:, ::vel_sample]
        U = np.zeros(len(vel_points[0]))
        V = np.zeros(len(vel_points[0]))
        W = np.zeros(len(vel_points[0]))
        for i in np.arange(0, len(vel_points[0])):
            dir_ = vel_points[3:, i] / np.linalg.norm(vel_points[3:, i])
            U[i] = dir_[0]
            V[i] = dir_[1]
            W[i] = dir_[2]
        q = ax.quiver(vel_points[0], vel_points[1], vel_points[2], U, V, W, length=0.04, normalize=True,colors='k')


    plt.show()




def plot_train_test_4d_demo_pos(p_train, att, p_test, **argv):


    t_tol = 2.5

    dt = 10E-3

    label_list = ['x', 'y', 'z']
    # colors = ['black', 'orchid', 'cornflowerblue', 'seagreen']
    # colors = ['black', 'darkred', 'peru']

    colors = ['black', 'darkviolet', 'mediumblue', 'lightsalmon']
    
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.figure.set_size_inches(6, 3.5)


    L = p_train.shape[0]

    for l in range(L):
        p_l = p_train[l, 0]

        p_l = p_l + np.tile(att, (2, p_l.shape[1]))

        for k in range(3):
            idx_l = np.linspace(0, t_tol, num=p_l.shape[1], endpoint=False)

            ax.plot(idx_l, p_l[k, :], linewidth=1, color=colors[k], alpha=0.3)


    idx = np.linspace(0, t_tol, num=p_test.shape[0], endpoint=False)


    for k in range(3):
        ax.plot(idx, p_test[:, k], color=colors[k], linewidth=2, label = label_list[k])

    # ax.xaxis.set_visible(False)
    # ax.set_xticklabels([])
    # ax.set_title("Position", fontsize = 30)
    # ax.set_xlabel("Time (sec)", fontsize=30)

    plt.savefig('position.png', dpi=600)
        


def _interp_index_list(q_list, index_list, interp=True, arr=True):
    L = len(index_list)

    index_list_interp = []

    if interp == True:
        ref = index_list[0]
        for l in np.arange(1, L):
            if index_list[l].shape[0] > ref.shape[0]:
                ref = index_list[l]
        N = ref[-1]-1

        for l in range(L):
            index_list_interp.append(np.linspace(0, N, num=index_list[l].shape[0]-1, endpoint=False, dtype=int))

        if arr==False:
            return index_list_interp

    elif interp == False:
        for l in range(L):
            index_list_interp.append(index_list[l] - index_list[l][0])

    else:
        for l in range(L):
            if l != L-1:
                N = index_list[l+1][0] - index_list[l][0] 
            else:
                N = len(q_list) - index_list[l][0]
            index_list_interp.append(np.arange(0, N))
            

    return np.hstack(index_list_interp)
