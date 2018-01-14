from Budget import Budget
#FEATURE: Should I instantiate Budgets with a transactions object, date range, etc?  That removes most inputs from functions.  But its outside scope, too...

class Budgets(object):
    """
    Object to interact with a groupd of Budget objects
    """

    def __init__(self):
        """
        Initialize empty Budgets object
        """
        self.budgets = []

    def add_budget(self, b):
        """
        Add a Budget instance to the Budgets object

        :param b: A Budget instance
        :return: None
        """
        self.budgets.append(b)

    def display(self):
        """
        Display to screen the contents of this object
        :return: None
        """
        for b in self.budgets:
            print(b)

    def plot(self, trxs, moving_average=None, start=None, stop=None, saveloc='./', prefix=''):
        """
        Save PNGs for each Budget to saveloc.

        :param trxs: Transactions object to be interpreted using this budget
        :param moving_average: (Optional) Integer input representing the number of months over which to calculate a
                               moving average to be added to the figure.  If None, no moving average is plotted.
        :param start: Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      start of the month by Transactions.slice_by_date).  If None, will start with the oldest transaction
        :param stop:  Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      end of the month by Transactions.slice_by_date).  If None, will stop with the most recent transaction
        :param saveloc: Relative file path to save location
        :param prefix: String to prepend to each saved PNG.  If True, date will be prepended.
        :return: None
        """

        if prefix is True:
            raise NotImplementedError

#     def plot_budget(self, trxs, moving_average=None, plot_budget=True, color=None, start=None, stop=None, savefig=None):

        for b in self.budgets:
            savefig = saveloc + prefix + b.name
            b.plot_budget(trxs, moving_average=moving_average, start=start, stop=stop, savefig=savefig)