import seaborn as sns
import matplotlib.pyplot as plt


def bar_viz(df1, df2, sg_cols, lvl):
    # Prepare data for first character:
    stat1 = df1.iloc[[-1]][sg_cols].T.reset_index()
    stat1.rename(columns={stat1.columns[0]: 'stat', stat1.columns[1]: 'val'}, inplace=True)
    char1 = df1['Name'][0]
    class1 = df1.loc[df1.index[-1], 'Class']

    # Prepare data for first character:
    stat2 = df2.iloc[[-1]][sg_cols].T.reset_index()
    stat2.rename(columns={stat2.columns[0]: 'stat', stat2.columns[1]: 'val'}, inplace=True)
    char2 = df2['Name'][0]
    class2 = df2.loc[df2.index[-1], 'Class']

    # Determine axis limit:
    ax_lim = max(df1[sg_cols].max().max(), df2[sg_cols].max().max())

    # Plot bar comparison:
    bar_comp(stat1, char1, class1, stat2, char2, class2, lvl, ax_lim)


def bar_comp(comp1, char1, class1, comp2, char2, class2, lvl, ax_lim):
    fig, ax = plt.subplots(1, 2, figsize=(8, 4), dpi=200)
    ax.flatten()

    sns.barplot(x=comp1.val, y=comp1.stat, data=comp1,
                color="#0ce6eb", ax=ax[0])
    sns.barplot(x=comp2.val, y=comp2.stat, data=comp2,
                color="#0ce6eb", ax=ax[1])

    # Common formatting between axes:
    fig.patch.set_facecolor('black')
    fig.patch.set_alpha(0.8)
    sns.despine(left=True, right=True, bottom=True, top=True)
    for a in range(2):
        ax[a].patch.set_alpha(0.0)
        ax[a].set_xlabel('')
        ax[a].set_ylabel('')
        ax[a].set_xlim(0, ax_lim)
        change_height(ax[a], .35)

    # Left hand bar chart:
    ax[0].tick_params(top=False, bottom=False, left=False, right=False,
                       labelleft=True, labelbottom=False,
                       colors='white')
    ax[0].set_title('%s - %s (Lvl %s)' % (char1, class1, lvl), color='white', fontweight='bold')
    ax[0].bar_label(ax[0].containers[0], color='white', padding=3, size=12)

    # Right hand bar chart:
    ax[1].invert_xaxis()
    ax[1].tick_params(top=False, bottom=False, left=False, right=False,
                       labelleft=False, labelright=True, labelbottom=False,
                       colors='white')
    ax[1].set_title('%s - %s (Lvl %s)' % (char2, class2, lvl), color='white', fontweight='bold')
    ax[1].bar_label(ax[1].containers[0], color='white', padding=-20, size=12)

    plt.show()


# Source: https://stackoverflow.com/questions/34888058/changing-width-of-bars-in-bar-chart-created-using-seaborn-factorplot
def change_height(ax, new_value):
    for patch in ax.patches:
        current_height = patch.get_height()
        diff = current_height - new_value

        # we change the bar height
        patch.set_height(new_value)

        # we recenter the bar
        patch.set_y(patch.get_y() + diff * .6)


def line_viz(df1, df2, rate_type, stat):
    # Get character info:
    char1 = df1['Name'][0]
    char2 = df2['Name'][0]

    # ----- Visualization -----#
    fig, ax = plt.subplots(1, 2, figsize=(8, 4), dpi=200)
    ax.flatten()

    # Chosen overall rating:
    sns.lineplot(x=df1['int_lev'], y=df1[rate_type], data=df1,
                 color="gold", ax=ax[0])
    sns.lineplot(x=df2['int_lev'], y=df2[rate_type], data=df2,
                 color="pink", ax=ax[0])

    # Chosen specific statistic:
    sns.lineplot(x=df1['int_lev'], y=df1[stat], data=df1,
                 color="gold", ax=ax[1])
    sns.lineplot(x=df2['int_lev'], y=df2[stat], data=df2,
                 color="pink", ax=ax[1])

    # Common formatting between axes:
    fig.patch.set_facecolor('black')
    fig.patch.set_alpha(0.8)
    sns.despine(left=True, right=True, bottom=True, top=True)

    for a in range(2):
        ax[a].patch.set_alpha(0.0)
        ax[a].tick_params(top=False, bottom=False, left=False, right=False,
                          labelleft=True, labelbottom=True,
                          colors='white')
        ax[a].legend(labels=[char1, char2], loc='upper left')
        ax[a].set_xlabel('Internal Level', color='white')

    # Left hand line plot:
    ax[0].set_title('Overall Rating', color='white', fontweight='bold')
    ax[0].set_ylabel('Rating', color='white')

    # Right hand line plot:
    ax[1].set_title('%s' % stat, color='white', fontweight='bold')
    ax[1].set_ylabel('')

    plt.show()