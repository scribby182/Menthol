from Transactions import Transactions, monthdelta
import matplotlib.pyplot as plt
import pandas as pd

#FEATURE: Most functions take the same arguments (start, stop, moving average, trxs).  Should budget instances just be set for these?

class Budget(object):
    """
    Budget object for viewing a Transactions object in the context of a budget.
    """

    def __init__(self, amount = None, categories=None, name=None):
        """
        Initialize Budget instance

        :param amount: Monthly budgeted dollar amount of spending
        :param categories: List of categories to include in budget
        """
        self.categories = categories
        self.amount = amount
        if name is None:
            self.name = ", ".join(self.categories)
        else:
            self.name = name

    def __str__(self):
        """
        Return a string representation of the Budget
        :return: String
        """
        return f"{self.name:25s} | ${self.amount:<5.0f} | {str(self.categories)}"

    def plot_budget(self, trxs, moving_average=None, plot_budget=True, color=None, start=None, stop=None, savefig=None):
        """
        Plot spending on a budget, optionally including the budget amount and an N-monthly moving average of spending.

        :param trxs: Transactions object to be interpreted using this budget
        :param moving_average: (Optional) Integer input representing the number of months over which to calculate a
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

        ax.bar(sum_monthly.df['Date'].as_matrix(), sum_monthly.df['Amount'].as_matrix(), width=10,
               label=f'{self.name}', color=color)

        # Plot rolling average, if requested
        if moving_average is not None:
            moving = sum_monthly.moving_average(n=moving_average)
            ax.plot(moving.df['Date'].as_matrix(), moving.df['Amount'].as_matrix(), color=color,
                    label=f'{self.name} {moving_average}-month average', ls='--')

        # Plot budget, if requested
        if plot_budget:
            ax.plot(date_range, [self.amount] * 2, color=color, ls=':', label=f'{self.name} Budget (${self.amount})')
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

        :param trxs: The Transactions object to use as the source for data
        :param moving_average: (Optional) Integer number of months over which to apply a moving average to the returned
                               data
        :param start: Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      start of the month by Transactions.slice_by_date).  If None, will start with the oldest transaction
        :param stop:  Datetime or Date object for the starting date of the intervals to plot (will be rounded to the
                      end of the month by Transactions.slice_by_date).  If None, will stop with the most recent transaction
        :return: Transactions instance
        """
        # TODO: Need test code
        new_trxs = trxs.slice_by_date(start=start, stop=stop).slice_by_category(self.categories)
        new_trxs = new_trxs.by_month(combine_as=self.name)
        if moving_average is not None:
            new_trxs = new_trxs.moving_average(n=moving_average)
        return new_trxs

    def to_ds(self, trxs, moving_average=None, start=None, stop=None):
        """
        Make a Pandas Series of this budget, with attributes by date
        :param trxs: See other methods
        :param moving_average: See other methods
        :param start: See other methods
        :param stop: See other methods
        :return: Pandas Series
        """
        trxs = self.tabulate_transactions(trxs, moving_average=moving_average, start=start, stop=stop)


        ds = pd.Series({})