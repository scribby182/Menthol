import calendar
import numpy as np
import csv
import pandas as pd
from pprint import pprint

#FEATURE: Change summarize to moving_average.

class Transactions(object):
    """
    Object to contain and interact with a Mint CSV file of Transactions
    """

    MINT_DTYPES = {
        "Description": "object",
        "Original Description": "object",
        "Amount": "float64",
        "Transaction Type": "object",
        "Category": "object",
        "Account Name": "object",
        "Labels": "object",
        "Notes": "object",
        }


    def __init__(self):
        """
        Initialize instance of class
        """
        self.df = None

    def __len__(self):
        """
        Returns number of transactions in the object.

        :return: Integer length
        """
        if isinstance(self.df, pd.DataFrame):
            return len(self.df)
        else:
            return 0

    def transaction_as_str(self, i):
        """
        Return a string summarizing a transaction (a single row within this object)

        :param i: Integer index to return
        :return: String
        """
        d = self.df.iloc[i]
        ret = f"{d.name}: {d['Date']} | {d['Amount']} | {d['Description']} | {d['Category']}"
        return ret

    def __str__(self):
        """
        Write all transactions into a formatted string of rows.
        :return:
        """
        if len(self) == 0:
            string = "<empty Transactions object>"
        else:
            string = f"{self.transaction_as_str(0)}"

        for i in range(1, len(self)):
            string += f"\n{self.transaction_as_str(i)}"
        return string

    def slice_by_category(self, categories, return_anti_match=False):
        """
        Return a slice of the Transactions object, including transactions in any of the requested categories.
        :param categories:
        :return:
        """
        return self.slice_by_keys('Category', categories, return_anti_match=return_anti_match)

    def slice_by_keys(self, column, keys, return_anti_match=False):
        """
        Return a slice of the Transaction object containing only records that match a list of keys in a given column

        Can optionally provide the not-match, where returns only records that DO NOT match anything in keys

        :param column: The column to slice on
        :param keys: A list of keys to include in the returned Transactions instance
        :param return_anti_match: If False, return records that match a key in keys.
                                 If True, return records that DO NOT match a key in keys.
        :return: A new Transactions instance
        """
        trxs = Transactions()

        # Initialize an all-false boolean index
        rows = self.df.index == None

        # Grab anything that was already matched (True in rows) or matches this cat
        if not isinstance(keys, list):
            raise ValueError(f"Input keys is a {type(keys)}, must be list")
        for k in keys:
            rows = (rows) | (self.df.loc[:, column] == k)

        # Invert the returned rows if required
        if return_anti_match:
            rows = ~rows

        trxs.df = self.df.loc[rows]

        return trxs

    def slice_by_date(self, start=None, stop=None, increment=None):
        """
        Slice the Transactions object by a date range, returning a new Transactions object with a copy of the DataFrame.

        :param start: (Optional) Start of date range, in date format.  If omitted, range starts at earliest record
        :param stop: (Optional) End date for range, in date format.   If omitted, range ends at latest record
        :param incremenet: Not implemented (not sure what it would mean here)
        :return: A new Transactions object
        """
        # Validate inputs
        if increment is not None:
            raise NotImplementedError

        if start is not None and stop is not None:
            if start > stop:
                raise ValueError("start ({0}) must be before stop ({1})".format(start, stop))

        newtrxs = Transactions()

        if start is None:
            start = self.df['Date'].min()
        if stop is None:
            stop = self.df['Date'].max()

        rows = (self.df['Date'] >= start) & (self.df['Date'] <= stop)
        df_temp = self.df.loc[rows, :]

        # Do I need a copy here?  never sure with pd.dataframes...
        newtrxs.df = df_temp
        return newtrxs

    def sum(self):
        if isinstance(self.df, pd.DataFrame):
            return self.df['Amount'].sum()
        else:
            return 0.0

    def by_month(self, ignore_blanks = True, combine_as=False, start=None, stop=None):
        """
        Return a new Transactions file that has a single entry for all spending in each categoriy per month.

        :param ignore_zero: If True, all categories that have zero transactions in a given month will be ignored.  If
                            False, an entry of $0 spending will be included in the returned Transactions item.
        :param combine_as: Sums monthly transactions in all categories into a new category named by combine_as.
        :param start: Starting date of the intervals to return (will be rounded to the start of the month)
                      If None, will start with the oldest transaction
        :param stop: End date of the intervals to return (will be rounded to the end of the month)
                      If None, will stop with the most recent transaction
        :return: Transactions instance
        """
        if start is None:
            start = self.df['Date'].min().replace(day=1)
        if stop is None:
            stop = self.df['Date'].max()

        # Build intervals to examine data over
        # Incrementing by 0 months without other arguments sets to the end of current month
        intervals = [(start, monthdelta(start, 0))]
        while intervals[-1][-1] < stop:
            next_start = monthdelta(intervals[-1][0], 1, day=1)
            intervals.append((next_start, monthdelta(next_start, 0)))

        categories = self.categories
        # List of data Series to make into DataFrame
        dss = []

        for interval in intervals:
            # Slice to this date range
            trxs = self.slice_by_date(interval[0], interval[1])
            # Get average spending for each category in this range
            dss_temp = []
            for cat in categories:
                this_cat = trxs.slice_by_category([cat])
                if len(this_cat) > 0 or ignore_blanks is False:
                    amount = this_cat.sum()
                    dss_temp.append(pd.Series({'Date': interval[1], 'Amount': amount, 'Category': cat, 'Description': f"1-month Summation"}))
            if combine_as:
                ds = pd.Series({'Date': interval[1], 'Amount': 0, 'Category': combine_as, 'Description': f"1-month Summation"})
                for this_ds in dss_temp:
                    ds.Amount += this_ds.Amount
                dss.append(ds)
            else:
                dss.extend(dss_temp)
        df = pd.DataFrame(dss)
        trxs_new = Transactions()
        trxs_new.df = df
        return trxs_new

    def moving_average(self, by='months', n=1, start=None, stop=None):
        """
        Return a DataFrame summarizing the rolling average over n_months of spending in each category.

        Dates in the returned DataFrame are the month/year of the last day in each interval.  Columns are the categories
        :param by: Type of increment to average over (currently supports only "months")
        :param n: Number of increments of 'by' to average over (days, months, years...)
        :param start: Starting date of the intervals to return (will be rounded to the start of the month)
                      If None, will start with the oldest transaction
        :param stop: End date of the intervals to return (will be rounded to the end of the month)
                      If None, will stop with the most recent transaction
        :return:
        """
        if by != 'months':
            raise NotImplementedError
        # FEATURE: Should this function return intervals starting at start (so for n_months > 1, this interval would be incomplete) or from start + n_months - 1?
        # Get start and end dates, if not specified.  Use first and last purchase.
        if start is None:
            start = self.df['Date'].min().replace(day=1)
        if stop is None:
            stop = self.df['Date'].max()

        # Build intervals to examine data over
        intervals = [(start, monthdelta(start, n - 1))]

        while intervals[-1][-1] < stop:
            next_start = monthdelta(intervals[-1][0], 1, day=1)
            intervals.append((next_start, monthdelta(next_start, n - 1)))

        categories = self.categories
        trxs_new = Transactions()
        # List of data Series to make into DataFrame
        dss = []

        for interval in intervals:
            # Slice to this date range
            trxs = self.slice_by_date(interval[0], interval[1])
            # Get average spending for each category in this range
            for cat in categories:
                amount = trxs.slice_by_category([cat]).sum() / float(n)
                dss.append(pd.Series({'Date': interval[1], 'Amount': amount, 'Category': cat, 'Description': f"{n}-month Average"}))
        df = pd.DataFrame(dss)
        trxs_new.df = df
        return trxs_new

    def get_daterange(self):
        """
        Return a tuple with dates of the first and last transactions in this object, as Datetime objects.

        :return: Tuple of (Datetime, Datetime)
        """
        return (self.df['Date'].min(), self.df['Date'].max())

    @classmethod
    def from_csv(cls, csv_file):
        """
        Initialize instance from a Mint-formatted csv file of transactions

        :param csv_file: Transaction file name
        :return: Instance of Transactions class
        """
        # Read csv
        df = pd.read_csv(csv_file, skipinitialspace = True,  quoting = csv.QUOTE_ALL, parse_dates = ['Date'],
                         dtype = cls.MINT_DTYPES)

        # Convert Amount column into signed amount
        df.loc[:, 'Amount'] = df.apply(signed_amount, axis = 1)

        trxs = Transactions()
        trxs.df = df
        return trxs

    @property
    def categories(self):
        """
        Returns an ndarray of the categories used in this Transactions object
        """
        try:
            return self.df['Category'].unique()
        except KeyError:
            return np.array([])

# Helper functions
def signed_amount(ds):
    if ds['Transaction Type'] == 'credit':
        return ds['Amount']
    elif ds['Transaction Type'] == 'debit':
        return -ds['Amount']
    else:
        raise ValueError(f"Invalid transaction_type {ds.transaction_type}")

def monthdelta(date, delta, day=None):
    """
    Return a date object that is delta months away from date.

    :param date:
    :param delta:
    :param day: If int, this specifics the day of the month to be returned (eg: day=5 means day 5).  If None, will
                return the last day of the month.
    :return:
    """
    m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
    if not m:
        m = 12
    if day is None:
        date = lastday(date.replace(day=1, month=m, year=y))
    else:
        date = date.replace(day=day, month=m, year=y)
    return date

def lastday(date):
    """
    Returns a datetime object for the last day of the month in date.

    :param date: Datetime object
    :return: Datetime object
    """
    d = calendar.monthrange(date.year, date.month)[1]
    return date.replace(day=d)