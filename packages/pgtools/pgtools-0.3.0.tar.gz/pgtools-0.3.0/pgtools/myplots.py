import os
import matplotlib
import seaborn
import matplotlib.pyplot as plt
import numpy
import scipy
import scipy.stats

from . import toolbox

FIG_EXTS = ('png', 'pdf')
PPT_16x9_FULL_BOX = (11.5, 4.75)  # size to fill a content box for default layout of a 16x9 powerpoint slide


def plot_cc(start, signal, peak_locations=[], fname=''):
    """
    Designed for plotting cross-correlation values. Given a segment of the cross-correlation signal and the coordinate of its
    start point, it will plot the signal strength and denote the peak location.
    """
    end = start + len(signal)
    seaborn.set_style('whitegrid')
    fig, ax = plt.subplots(1)
    xs = range(start + 1, end + 1)
    ax.plot(xs, signal)
    ax.set_xlim(start, end)
    ax.set_xlabel('Fragment length (bp)', fontsize=14)
    ax.set_ylabel('Cross-correlation', fontsize=14)

    if not peak_locations:
        peak_locations = [numpy.argmax(signal) + start + 1]

    for peak in peak_locations:
        peak_line = matplotlib.lines.Line2D(xdata=(peak, peak), ydata=(0, ax.get_ylim()[1]), linestyle="--", color='r')
        ax.add_line(peak_line)

    text_x = start + (end - start) * 0.95
    text_y = ax.get_ylim()[1] * 0.9

    ax.text(x=text_x, y=text_y, s='Peaks: {}'.format(', '.join([str(p + 1) for p in peak_locations])),
            horizontalalignment='right', fontsize=14)
    if fname:
        for fig_ext in FIG_EXTS:
            fig.savefig('{}.{}'.format(fname, fig_ext), dpi=600)


def my_bars(df, name_column='', fname_prefix='', title='', ylim=None, ylabel=''):
    """
    Given a DataFrame, will produce a bar graph for each column
    Bars will be labeled with the values in <name_column>. If <name_column>
    is not given, use the index
    """

    X_PAD = 0.05
    bar_width = (1 - X_PAD * len(df.index)) / len(df.index)
    TICKS_FONT = matplotlib.font_manager.FontProperties(family='arial', style='italic', size=12, weight='normal',
                                                        stretch='normal')

    col_list = [col for col in df.columns if col != name_column]

    fig, ax = plt.subplots(1, len(col_list), figsize=(3 * len(col_list), 3))

    max_value = max([df[col].max() for col in df.columns])
    min_value = min([df[col].min() for col in df.columns])

    if min_value >= 0 and max_value <= 1:
        y_lim = (0, 1)
    else:
        if min_value < 0:
            y_lim = (min_value * 1.1, max_value * 1.1)
        else:
            y_lim = (0, max_value * 1.1)

    for i, col in enumerate(sorted(col_list)):
        data_series = df[col].dropna()

        centers = numpy.linspace(X_PAD, 1 - X_PAD, num=len(data_series) + 2)[1:-1]
        lefts = [c - (bar_width / 2) for c in centers]

        ax[i].bar(lefts, data_series, width=bar_width)

        ax[i].set_ylim(*y_lim)
        ax[i].set_xlim(0, 1)
        ax[i].set_xticks(centers)

        if name_column:
            ax[i].set_xticklabels([df.ix[d, name_column] for d in data_series.index])
        else:
            ax[i].set_xticklabels(list(data_series.index))

        for l in ax[i].get_xticklabels():
            l.set_rotation(270)
            l.set_font_properties(TICKS_FONT)

        ax[i].grid(b=0, which='major', axis='x')

        if i == 0:
            ax[i].set_ylabel(ylabel)
        else:
            ax[i].set_yticklabels([])

        ax[i].set_title(col.split('_')[0])

    fig.text(x=0.5, y=1.2, s=title, ha='center', fontsize=20)

    if fname_prefix:
        for fig_ext in FIG_EXTS:
            fig.savefig('{}.{}'.format(fname_prefix, fig_ext), dpi=600)
    return fig


def kde_plot(data, ax=None):
    xs = numpy.linspace(data.min(), data.max())
    if not ax:
        fig, ax = plt.subplots(1)
    ax.plot(xs, scipy.stats.gaussian_kde(data)(xs))
    return ax


def my_hist2d(xs, ys, x_title='', y_title='', binsizes=[], x_lim=None, y_lim=None, norm=matplotlib.colors.LogNorm(),
              cmap='binary',
              fname_prefix='', PCC=None, overall_title='', show_PCC=True, show_title=True, fig_size=(8, 6),
              fig_exts=FIG_EXTS):
    seaborn.set_style('white')
    fig, ax = plt.subplots(1, 1, figsize=fig_size)

    max_x = max(xs)
    max_y = max(ys)
    min_x = min(xs)
    min_y = min(ys)

    if not x_lim:
        x_lim = (min_x, max_x)
    if not y_lim:
        y_lim = (min_y, max_y)

    x_span = x_lim[1] - x_lim[0]
    y_span = y_lim[1] - y_lim[0]

    if not binsizes:
        binsizes = (toolbox.iround(max_x), toolbox.iround(max_y))

    ax.hist2d(xs, ys, bins=binsizes, range=(x_lim, y_lim), norm=norm, cmap=cmap)
    ax.set_xlabel(x_title, fontsize=16)
    ax.set_ylabel(y_title, fontsize=16)

    if show_PCC:
        if not PCC:
            PCC = scipy.stats.pearsonr(xs, ys)[0]
        ax.text(x_span * 0.75 + min_x, y_span * 0.1 + min_y, s='PCC: {:.3}'.format(PCC), fontsize=16)

    if show_title:
        if overall_title:
            fig.suptitle(overall_title, fontsize=18)
        elif x_title and y_title:
            fig.suptitle('{} vs. {}'.format(x_title, y_title), fontsize=18)

    if fname_prefix:
        for fig_ext in fig_exts:
            print('Saving figure as {}'.format('{}.{}'.format(fname_prefix, fig_ext)))
            fig.savefig('{}.{}'.format(fname_prefix, fig_ext), dpi=600)
    return fig


def simple_profile(profile, fname_prefix='', color='k', fig_exts=('png', 'pdf')):
    # seaborn.set_style('white')
    fig, ax = plt.subplots(1, 1, figsize=(10, 1.2), facecolor='white', frameon=False)
    ax.bar(list(range(len(profile))), profile, width=1.0, linewidth=0, color=color)
    ax.set_frame_on(False)
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    if fname_prefix:
        for fig_ext in fig_exts:
            fig.savefig('{}.{}'.format(fname_prefix, fig_ext), dpi=600)
    return fig


def wig_plot(input_data, fname='', figsize=(6, 2), frame_on=False, color='k'):
    seaborn.set_style('white')
    size = len(input_data)
    fig, ax = plt.subplots(1, 1, figsize=figsize, facecolor='white', frameon=frame_on)
    max_height = max(input_data)
    ax.bar(list(range(size)), input_data, width=1.0, linewidth=0, color=color)
    # ax.set_frame_on(frame_on)
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    if fname:
        for fig_ext in FIG_EXTS:
            fig.savefig(os.path.join(IMG_OUTPATH, '{}.{}'.format(fname, fig_ext)), dpi=600)
