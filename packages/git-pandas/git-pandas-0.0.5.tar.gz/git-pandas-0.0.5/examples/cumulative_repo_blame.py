import matplotlib.pyplot as plt
import os
import json
from gitpandas import Repository, ProjectDirectory
import matplotlib
matplotlib.style.use('ggplot')

__author__ = 'willmcginnis'


if __name__ == '__main__':
    g = Repository(working_dir=os.path.abspath('../../git-pandas'), verbose=True)

    b = g.cumulative_blame(branch='master', extensions=['py'], ignore_dir=['docs'], limit=None, skip=None)

    ax = b.plot(kind='area', stacked=True)
    plt.title('Cumulative Blame')
    plt.xlabel('date')
    plt.ylabel('LOC')
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()