import pickle
import matplotlib.pyplot as plt

def open_and_fit_pickle_fig(pkl_path):
    with open(pkl_path, 'rb') as f:
        fig = pickle.load(f)
    fig.set_size_inches(10, 6, forward=True)
    print(fig.axes)
    for ax in fig.axes:
        print("Lines:", ax.get_lines())
        print("Children:", ax.get_children())

    for ax in fig.get_axes():
        ax.set_xlim(auto=True)
        ax.set_ylim(auto=True)
        ax.relim()
        ax.autoscale(enable=True)
        ax.autoscale_view(True, True, True)
        try:
            ax.set_aspect('auto')
        except Exception:
            pass
    fig.tight_layout()
    fig.canvas.draw()
    plt.show(block=True)  # This will block script exit until you close the window
