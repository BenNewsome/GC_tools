"""
Settings and functions to help with plotting.
"""
import logging

class plot_settings:
    '''
    Class containing plot settings which can be passed to plotting functions
    '''
    def __init__(self):
        '''
        Creates the default plot settings to use in matplotlib
        '''

        logging.info('Creating a plot settings class')

        self.tick_size  = 18
        self.title_size = 26
        self.filename   = "test.png"
        self.tick_axis  = "y"
        self.tick_type  = "major"
        self.labelleft  = "no"
        
        return

def multi_line_plot( dataset, x_ticks=None, y_ticks=None, plot_settings=None ):
    '''
    Creates a set of line plots from a list of lists.
    '''

    logging.info('Plotting a multi line plot.')

    # Check if we have plottable data.
    assert type(dataset) == list, "The x_data is not a list!"
    for data in dataset:
        assert type(data) == dict, "An item in x_data is not a dict."

    import matplotlib
#    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    if plot_settings == None:
        from .plotting import plot_settings as get_plot_settings
        plot_settings = get_plot_settings()


    figure = plt.figure()


    for data in dataset:
        x_data = data['x_data']
        y_data = data['y_data']
        if 'name' in data:
            label = data['name']
        else:
            label = None
        print x_data
        print y_data
        plt.plot( x_data, y_data, label=label )

    if not x_ticks==None:
        plt.xticks( x_ticks[0], x_ticks[1] )
    if not y_ticks==None:
        plt.yticks( y_ticks[0], y_ticks[1] )
    plt.legend()
#    plt.yticks( y_data, y_ticks )        

    figure.savefig(plot_settings.filename)

    return

