import pandas as pd
import copy
from Transaction import Transaction

class Transactions(object):
    """
    Object to contain and interact with a group of Transaction instances
    """

    def __init__(self):
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
        # print("d before printing:")
        # print(d)
        ret = f"{d.name}: {d['date']} | {d['signed_amount']} | {d['description']} | {d['category']} | {d['account']}"
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

    def __eq__(self, other):
        """
        Compare two Transactions objects.  Returns true if both have the same transactions in the same order.

        Sorts the dataframe column order, so column order does not matter in the match.

        :return: Boolean
        """
        print("self: ")
        print(self.df)
        print('other: ')
        print(other.df)
        return self.df.reindex_axis(sorted(self.df.columns), axis=1).equals(
               other.df.reindex_axis(sorted(other.df.columns), axis=1))

    def add_transaction(self, trx):
        """
        Setter to add a transaction to the object.

        :param trx: An instance of Transaction
        :return: None
        """
        if not isinstance(trx, Transaction):
            raise TypeError("Invalid type for trx ('{0}').  Must be instance of Transaction".format(type(trx)))
        # Store all data in the order of trx.fields, with the signed amount appended to the end.
        # Adding signed_amount could be cleaner...
        data = trx.to_list() + [trx.signed_amount]
        columns = trx.fields + ["signed_amount"]
        df = pd.DataFrame(data=[data], columns=columns)

        if self.df is None:
            self.df = df
        else:
            self.df = self.df.append(df, ignore_index=True)

    def slice_by_date(self, start=None, stop=None, incremenet=None):
        """
        Slice the Transactions object by a date range, returning a new Transactions object with a copy of the DataFrame.

        :param start: (Optional) Start of date range, in datetime format.  If omitted, range starts at earliest record
        :param stop: (Optional) End date for range, in datetime format.   If omitted, range ends at latest record
        :param incremenet: Not implemented (not sure what it would mean here)
        :return: A new Transactions object
        """
        # Validate inputs
        if incremenet is not None:
            raise NotImplementedError

        if start is not None and stop is not None:
            if start > stop:
                raise ValueError("start ({0}) must be before stop ({1})".format(start, stop))

        newtrxs = Transactions()

        if start is None:
            start = self.df['date'].min()
        if stop is None:
            stop = self.df['date'].max()

        rows = (self.df['date'] >= start) & (self.df['date'] <= stop)
        print("rows: ")
        print(rows)
        df_temp = self.df.loc[rows, :]
        print('df_temp')
        print(df_temp)

        newtrxs.df = df_temp
        return newtrxs

    def to_csv(self, csv_file, header=True, data_map=None):
        """
        Export transactions in a Transactions instance to a csv file, optionally with a header.

        :param csv_file: Filename to export
        :param header: Boolean to set whether the header is included
        :param data_map: Dictionary that maps data fields to columns in the output file (NOT IMPLEMENTED)
        :return: None
        """
        self.df.to_csv(csv_file, index=False)

    @classmethod
    def from_csv(cls, csv_file, sep='\s*,\s*'):
        """
        Load a set of transactions from a csv file and return as a Transactions instance.

        :param csv_file: Filename of the csv file to read transactions from
        :param sep: Separator between fields (in Pandas DataFrame read_csv sep format, eg: can be a regular expression)
        :return: An instance of Transactions
        """
        trxs = Transactions()
        # Parse with Python engine to support regex separator
        trxs.df = pd.read_csv(csv_file, sep=sep, parse_dates=['date'], dtype={'amount': 'float64'}, engine='python')
        if len(trxs) > 0:
            def signed_amount(ds):
                if ds.transaction_type == 'credit':
                    return ds.amount
                elif ds.transaction_type == 'debit':
                    return -ds.amount
                else:
                    raise ValueError(f"Invalid transaction_type {ds.transaction_type}")
        else:
            raise ValueError(f"No data found in csv file {csv_file}")
        trxs.df['signed_amount'] = trxs.df.apply(signed_amount, axis=1)
        return trxs

    @classmethod
    def sample_trxs(cls, n=10, **kwargs):
        """
        Returns a sample Transactions with n Transaction objects that have semi-random data.

        :param n: Number of records to include in the returned Transactions instance
        :param kwargs: Additional arguments will be passed to the Transaction.sample_trx() method, which allows the
                       user to set some data within the random objects

        :return: A Transactions instance
        """
        trxs = cls()
        for i in range(n):
            trxs.add_transaction(Transaction.sample_trx(**kwargs))
        return trxs
