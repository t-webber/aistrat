import matplotlib.pyplot as plt
from IPython import display

plt.ion()


def plot(scores, mean_scores,max,mean_max):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.subplot(121)
    plt.title('Evalutation')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.subplot(122)
    plt.title('Evalutation')
    plt.xlabel('Number of Games')
    plt.ylabel('Max')
    plt.plot(max)
    plt.plot(mean_max)
    plt.ylim(ymin=0)
    plt.text(len(max)-1, max[-1], str(max[-1]))
    plt.text(len(mean_max)-1, mean_max[-1], str(mean_max[-1]))
    plt.show(block=False)
    plt.pause(.1)