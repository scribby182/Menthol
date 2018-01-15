from Budget import Budget
import os
import datetime

#FEATURE: Should I instantiate Budgets with a transactions object, date range, etc?  That removes most inputs from functions.  But its outside scope, too...  Could be optionally defined in self.trxs, but only used if input argument is not given during invocation (or could have two separate methods of invokation...)

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

    def get_budgets(self):
        """
        Return a list of budgets in this object
        :return: List of Budget instances
        """
        return self.budgets

    def add_budgets(self, bs, as_copy=True):
        """
        Add one or more Budget instances to this object by passing an existing Budgets instance.

        :param bs: Another Budgets instance
        :return:
        """
        for b in bs.get_budgets():
            self.add_budget(b)

    def display(self):
        """
        Display to screen the contents of this object
        :return: None
        """
        for b in self.get_budgets():
            print(b)

    def plot(self, trxs, moving_average=None, start=None, stop=None, saveloc='./', prefix='', normalize_dates=True):
        """
        Save PNGs for each Budget to saveloc.

        :param trxs: Transactions object to be interpreted using this budget
        :param moving_average: (Optional) List of integers representing the number of months over which to calculate a
                               moving average to be added to the figure.  If None, no moving average is plotted.
        :param start: Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      start of the month by Transactions.slice_by_date).  If None, will start with the oldest transaction
        :param stop:  Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      end of the month by Transactions.slice_by_date).  If None, will stop with the most recent transaction
        :param saveloc: Relative file path to save location
        :param prefix: String to prepend to each saved PNG.  If True, date will be prepended.
        :param normalize_dates: If True, find the min and max date of the data and make all plots over
                                that date range
                                Note: Specifying start and/or stop will override any value set by normalize_dates
        :return: None
        """
        if normalize_dates:
            date_range = trxs.get_daterange()
            if start is None:
                start = date_range[0]
            if stop is None:
                stop = date_range[1]

        if prefix is True:
            prefix = datetime.datetime.today().strftime("%Y-%m-%d_")

        if not os.path.exists(saveloc):
            os.makedirs(saveloc)

        for b in self.get_budgets():
            savefig = saveloc + prefix + b.name
            print(f"Saving figure for {b.name} as {savefig}")
            print(f"Date range: {start} to {stop}")
            b.plot_budget(trxs, moving_average=moving_average, start=start, stop=stop, savefig=savefig)

    def get_transactions_in_budgets(self, trxs, return_anti_match=False):
        """
        Compute a slice of trxs that includes any transactions covered by at least one budget in this Budgets

        :param trxs: Transactions instance to search
        :param return_anti_match: If True, match everything that IS NOT covered by this Budgets
        :return: Transactions instance with all applicable transactions
        """
        categories = set()
        for b in self.get_budgets():
            for cat in b.categories:
                categories.add(cat)
        categories = list(categories)

        return trxs.slice_by_category(categories, return_anti_match=return_anti_match)

    def get_transactions_not_in_budgets(self, trxs):
        """
        Compute a slice of trxs that includes any transactions not covered by at least one budget in this Budgets

        :param trxs: Transactions instance to search
        :return: Transactions instance with all applicable transactions
        """
        return self.get_transactions_in_budgets(trxs, return_anti_match=True)
