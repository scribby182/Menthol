from Budget import Budget
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product
from Transactions import monthdelta

#FEATURE: Should I instantiate Budgets with a transactions object, date range, etc?  That removes most inputs from functions.  But its outside scope, too...  Could be optionally defined in self.trxs, but only used if input argument is not given during invocation (or could have two separate methods of invokation...)

class Budgets(object):
    """
    Object to interact with a groupd of Budget objects
    """

    def __init__(self, name="Unnamed Budgets"):
        """
        Initialize empty Budgets object
        """
        self.budgets = []
        self.name = name

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

    def extend(self, bs, as_copy=True):
        """
        Extend this object by adding all Budget objects from bs to this Budgets instance

        :param bs: Another Budgets instance
        :return:
        """
        for b in bs.get_budgets():
            self.add_budget(b)

    def add_budgets(self, bs):
        """
        Add a Budgets instance to this object by converting it to a single Budget and storing.

        This method uses the Budgets.to_budget() method to change bs into a Budget

        :param bs: A Budgets instance
        :return: None
        """
        self.add_budget(bs.to_budget())

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

    def to_df(self, trxs, moving_average=None, start=None, stop=None, return_relative=True):
        """
        Returns a DataFrame containing one or more moving average value for each month for all budgets in this instance

        Results are arranged using a multi-index of date and moving average

        :param trxs: Transactions instance
        :param moving_average: List of one or more moving averages to include.  If None, will use [1] by default
        :param start: (Optional) Start of date range, in date format.  If omitted, range starts at earliest record
                                 in all trxs transactions.
        :param stop: (Optional) End date for range, in date format.   If omitted, range ends at latest record in trxs
        :param return_relative: Optionally return values relative to their budget amount (eg: budget.amount=-5 and total
                                is -11, returned is -6)

        :return: Dataframe
        """
        #TODO: This returns NaN for some fields, I think because the dates in each budget are not the full date range.  Need to address this.
        if moving_average is None:
            moving_average = [1]

        if start is None or stop is None:
            daterange = trxs.get_daterange()
            if start is None:
                start = daterange[0]
            if stop is None:
                stop = daterange[1]

        dss = []
        for b in self.get_budgets():
            dss.append(b.to_ds(trxs, moving_average=moving_average, start=start, stop=stop, return_relative=return_relative))
        df = pd.DataFrame(dss)
        return df

    def heatmap_table(self, trxs, moving_average=None, start=None, stop=None, saveloc='./budget', return_relative=True,
                      vmin=-200, vmax=200):
        """
        Saves a Seaborn Heatmap formatted table of the Budgets to a file.

        :param trxs: Transactions object to be interpreted using this budget
        :param moving_average: (Optional) List of integers representing the number of months over which to calculate a
                               moving average to be added to the figure.  If None, no moving average is plotted.
        :param start: Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      start of the month by Transactions.slice_by_date).  If None, will start with the month of the
                      oldest transaction that includes a full period of time for the requested moving average (eg, if
                      moving_average=[4] and oldest transaction is January 2017, the first returned value will be April
                      2017)
        :param stop:  Datetime or Date object for the starting date of the intervals to display (will be rounded to the
                      end of the month by Transactions.slice_by_date).  If None, will stop with the most recent
                      transaction
        :param saveloc: Relative file path and name to save location
        :param return_relative: Optionally return values relative to their budget amount (eg: budget.amount=-5 and total
                                is -11, returned is -6)
        :param vmin, vmax: Min (max) value for the color range

        :return: None
        """
        if start is None:
            start = monthdelta(trxs.get_daterange()[0], +(max(moving_average)-1), 1)

        df = self.to_df(trxs, moving_average=moving_average, start=start, stop=stop, return_relative=return_relative)
        months = len(df.columns)
        width = 6 + months
        height = 4 + months / 1.25
        fig, ax = plt.subplots(figsize=(width, height))

        # Create readable x-tick labels in format "Mon-YYYY | MovingAverage"
        dates = [f"{date[0].strftime('%b-%Y')}" for date in list(df.columns)]
        xticklabels = [" | ".join((x[0], str(x[1]))) for x in product(dates, moving_average)]

        sns.heatmap(df, annot=True, ax=ax, fmt='.2f', vmin=vmin, vmax=vmax, center=0, cmap=sns.color_palette("RdYlGn"),
                    xticklabels=xticklabels)

        # Enlarge tick size (need a better way of setting this size?
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(14)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(14)
        fig.savefig(saveloc)

    def to_budget(self, name=None, amount_type="Monthly"):
        """
        Returns all of this object's Budget instances combined as a single new Budget

        :return:
        """
        #TODO Check for duplicates during merger?  Maybe add this to Add Budget?
        if name is None:
            name = self.name
        categories = []
        amount = 0
        budgets = self.get_budgets()
        for b in budgets:
            amount += b.amount
            categories.extend(b.categories)
            # print(f"Found budget {b.name}: {b.amount} budgeted for categories {b.categories}")
            # print(f"New summation: {amount} for categories {categories}")
        return Budget(amount, categories, name=name, amount_type=amount_type)

