from Transactions import Transactions, monthdelta, month_intervals
import matplotlib.pyplot as plt
import pandas as pd
from pprint import pprint
import numpy as np

#FEATURE: Most functions take the same arguments (start, stop, moving average, trxs).  Should budget instances just be set for these?

class Budget(object):
    """
    Budget object for viewing a Transactions object in the context of a budget.
    """

    def __init__(self, amount, categories, name=None, amount_type="Monthly"):
        """
        Initialize Budget instance

        :param amount: Monthly budgeted dollar amount of spending
        :param categories: List of categories to include in budget
        :param amount_type: Specifies how amount is specified, eg:
                                Monthly: X dollars per month
                                Yearly: X dollars per year (converted internally to monthly)
        """
        self.categories = categories
        if amount_type == "Yearly":
            amount = amount / 12.0
        elif amount_type == "Monthly":
            pass
        else:
            raise ValueError("Invalid value for amount_type ('{0}')".format(amount_type))
        self.amount = amount
        if name is None:
            self.name = ", ".join(self.categories)
        else:
            self.name = name

    def to_str(self, amount=True, categories=True):
        """
        Return a string representation of the Budget, optionally including some pieces
        :return:
        """
        ret = f"{self.name:30s}"
        if amount:
            ret += f" | ${self.amount:>8.2f}"
        if categories:
            ret += f" | {str(self.categories)}"
        return ret

    def __str__(self):
        """
        Return a string representation of the Budget
        :return: String
        """
        return self.to_str()

    def plot_budget(self, trxs, moving_average=None, plot_budget=True, color=None, start=None, stop=None, savefig=None):
        """
        Plot spending on a budget, optionally including the budget amount and an N-monthly moving average of spending.

        :param trxs: Transactions object to be interpreted using this budget
        :param moving_average: (Optional) List of integers representing the number of months over which to calculate a
                               moving average to be added to the figure.  If None, no moving average is plotted.
        :param color: Optional color of the bars and lines to be plotted
        :param start: Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      start of the month by Transactions.slice_by_date).  If None, will start with the oldest transaction
        :param stop:  Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      end of the month by Transactions.slice_by_date).  If None, will stop with the most recent transaction
        :return: Figure and axes objects
        """
        # FEATURE: Add inputs for Fig, ax, to be able to plot multiple things on the same figure/axes
        fig, ax = plt.subplots()

        # Plot monthly spending as bars
        sum_monthly = self.tabulate_transactions(trxs, moving_average=None, start=start, stop=stop)
        date_range = sum_monthly.get_daterange()
        date_range = (monthdelta(date_range[0], delta=-1, day=None), monthdelta(date_range[1], delta=1, day=None))

        ax.bar(sum_monthly.df['Date'].values, sum_monthly.df['Amount'].values, width=10,
               label=f'{self.name}', color=color)

        # Plot budget, if requested
        if plot_budget:
            ax.plot(date_range, [self.amount] * 2, color=color, ls='-', label=f'{self.name} Budget (${self.amount})')

        # Plot rolling average, if requested
        if moving_average is not None:
            for ma in moving_average:
                moving = sum_monthly.moving_average(start=start, stop=stop, n=ma)
                ax.plot(moving.df['Date'].values, moving.df['Amount'].values, color=color,
                        label=f'{self.name} {ma}-month average', ls='--')

        fig.autofmt_xdate(bottom=0.2, rotation=30, ha='right')

        if savefig is not None:
            if savefig is True:
                savefig = self.name
            ax.legend()
            fig.savefig(savefig)

        return fig, ax

    def tabulate_transactions(self, trxs, moving_average=None, start=None, stop=None):
        """
        Return a Transactions instance with a summation of all transactions in trxs for this budget, summed by month.

        Optionally apply a moving average to the monthly values returned.

        If start and a moving average are both specified, the moving average will be computed using the requested date
        range PLUS the (moving_average-1) months before the range.  This is done to attempt to get a true n-month moving
        average when slicing dates (otherwise the first n-1 months will be partial averages and unusually low values).
        To avoid this behaviour, slice the trxs object by date before passing to tabulate_transactions

        :param trxs: The Transactions object to use as the source for data
        :param moving_average: (Optional) Integer number of months over which to apply a moving average to the returned
                               data
        :param start: Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      start of the month by Transactions.slice_by_date).  If None, will start with the oldest transaction
        :param stop:  Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      end of the month by Transactions.slice_by_date).  If None, will stop with the most recent transaction
        :return: Transactions instance
        """
        if moving_average is not None and start is not None:
            data_start = monthdelta(start, -(moving_average - 1), 1)
        else:
            data_start = start
        new_trxs = trxs.slice_by_date(start=data_start, stop=stop).slice_by_category(self.categories)
        new_trxs = new_trxs.by_month(start=data_start, stop=stop, combine_as=self.name)
        if moving_average is not None:
            new_trxs = new_trxs.moving_average(start=start, stop=stop, n=moving_average)
        return new_trxs

    def to_ds(self, trxs, moving_average=None, start=None, stop=None, return_relative=True):
        """
        Make a Pandas Series of this budget, with attributes in a multiindex of Date, Moving Average
        :param trxs: See other methods
        :param moving_average: See other methods
        :param start: (Optional) Start of date range, in date format.  If omitted, range starts at earliest record
                                 in trxs
        :param stop: (Optional) End date for range, in date format.   If omitted, range ends at latest record in trxs
        :param return_relative: If True, return all values relative to their budget (eg: if overspent, <0.  If
                                underspent, >0)
        :return: Pandas Series
        """
        #FEATURE: Need test code
        by_month = {}
        by_month_amounts = {}
        if moving_average is None:
            moving_average = [1]

        for ma in moving_average:
            by_month[ma] = self.tabulate_transactions(trxs, moving_average=ma, start=start, stop=stop)
            by_month_amounts[ma] = by_month[ma].get_amounts()
            if return_relative:
                for i in range(len(by_month_amounts[ma])):
                    by_month_amounts[ma][i] -= self.amount

        a_key = list(by_month.keys())[0]
        dates = by_month[a_key].get_dates()

        columns = pd.MultiIndex.from_product([dates, moving_average])

        data = []
        for i in range(len(by_month[a_key])):
            for ma in moving_average:
                data.append(by_month_amounts[ma][i])
        data = np.array(data)

        ds = pd.Series(data, index=columns, name=self.name + f" ({str(self.amount)})")
        return ds
