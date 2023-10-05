import matplotlib.pyplot as plt
import numpy as np


def plot_reference_trajectories_DS(Data, att, vel_sample, vel_size):
    fig = plt.figure(figsize=(16, 10))
    M = len(Data) / 2  # store 1 Dim of Data
    if M == 2:
        ax = fig.add_subplot(111)
        ax.set_xlabel(r'$\xi_1$')
        ax.set_ylabel(r'$\xi_2$')
        ax.set_title('Reference Trajectory')

        # Plot the position trajectories
        plt.plot(Data[0], Data[1], 'ro', markersize=1)
        # plot attractor
        plt.scatter(att[0], att[1], s=100, c='blue', alpha=0.5)
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



def plot_incremental(new_data, prev_data):
    fig = plt.figure(figsize=(16, 10))

    ax = fig.add_subplot(projection='3d')
    ax.plot(prev_data[0], prev_data[1], prev_data[2], 'o', color='r', markersize=1.5,  label='original data')
    # ax.scatter(att[0], att[1], att[2], s=200, c='blue', alpha=0.5)
    ax.plot(new_data[0], new_data[1], new_data[2], 'o', color = 'magenta', markersize=1.5,  label='new data')

    
    ax.axis('auto')
    ax.set_title('Reference Trajectory')
    ax.set_xlabel(r'$\xi_1(m)$')
    ax.set_ylabel(r'$\xi_2(m)$')
    ax.set_zlabel(r'$\xi_3(m)$')
    
    # import matplotlib.patches as mpatches
    # red_patch = mpatches.Patch(color='red', label='The red data')
    # ax.legend(handles=[red_patch])
    import matplotlib.lines as mlines
    new_label = mlines.Line2D([], [], color='red',
                          linewidth=3, label='original data')
    old_label = mlines.Line2D([], [], color='magenta',
                        linewidth=3, label='new data')
    ax.legend(handles=[new_label, old_label])
    
    plt.show()

    # vel_points = Data[:, ::vel_sample]
    # U = np.zeros(len(vel_points[0]))
    # V = np.zeros(len(vel_points[0]))
    # W = np.zeros(len(vel_points[0]))
    # for i in np.arange(0, len(vel_points[0])):
    #     dir_ = vel_points[3:, i] / np.linalg.norm(vel_points[3:, i])
    #     U[i] = dir_[0]
    #     V[i] = dir_[1]
    #     W[i] = dir_[2]
    # q = ax.quiver(vel_points[0], vel_points[1], vel_points[2], U, V, W, length=0.04, normalize=True,colors='k')