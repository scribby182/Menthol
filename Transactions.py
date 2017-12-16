from Transaction import Transaction
import copy

# FEATURE: Likely makes sense to store transactions as a Pandas dataframe, but that isn't so good for practice...
# TODO: Convert Transactions to DataFrame for storage.  How should outward API look?  How do I store now, keep the trx or just the DataFrame?
# TODO: Does __eq__ work properly for DataFrame?  test!
# TODO: How should slicing API work for the Transactions class?

class Transactions(object):
    """
    Object to contain and interact with a group of Transaction instances
    """

    def __init__(self):
        self.transactions = []

    def __len__(self):
        """
        Returns length of Transactions instance, which is equivalent to the number of transactions contained in object.

        :return: Integer length
        """
        return len(self.transactions)

    def __str__(self):
        """
        Write all transactions into a formatted string of rows.
        :return:
        """
        if len(self) == 0:
            string = "<empty Transactions object>"
        else:
            string = "0: " + self.transactions[0].__str__() + "\n"

        for i in range(1, len(self)):
            string += str(i) + ": " + self.transactions[i].__str__() + "\n"
        return string

    def __eq__(self, other):
        """
        Compare two Transactions objects.  Returns true if both have the same transactions in the same order.

        Transaction similarity is evaluated using Transaction.__eq__, which returns True if objects contain the same
        data (the objects do not need to be the same object).

        :return: Boolean
        """
        if len(self) != len(other):
            return False

        # If the same length, we can traverse through self comparing to the corresponding element in other.  If nothing
        # is in disagreement, then we're good.
        equal = True
        for i in range(len(self.transactions)):
            if self.transactions[i] != other.transactions[i]:
                equal = False
                break
        return equal


    def add_transaction(self, trx):
        """
        Setter to add a transaction to the object.

        :param trx: An instance of Transaction
        :return: None
        """
        # FEATURE: Auto-sort transactions on add?  Or keep different sorted maps (by category, date, ...)?
        # FEATURE: Optional (on by default) make copy of transaction as you store it, rather than a view?
        if not isinstance(trx, Transaction):
            raise TypeError("Invalid type for trx ('{0}').  Must be instance of Transaction".format(type(trx)))
        self.transactions.append(trx)

    def slice_by_date(self, start=None, stop=None, incremenet=None, trx_as_copy=True):
        """
        Slice the Transactions object by a date range, returning a new Transactions object.

        :param start: (Optional) Start of date range, in datetime format.  If omitted, range starts at earliest record
        :param stop: (Optional) End date for range, in datetime format.   If omitted, range ends at latest record
        :param incremenet: Not implemented (not sure what it would mean here)
        :param trx_as_copy: If True, returns a Transactions object with new copies of all relevant Transaction instances
                            If False, returns a Transactions object that references the original relevant Transaction
                            instances
        :return: A new Transactions object
        """
        # Validate inputs
        if incremenet is not None:
            raise NotImplementedError

        if start is not None and stop is not None:
            if start > stop:
                raise ValueError("start ({0}) must be before stop ({1})".format(start, stop))

        newtrxs = Transactions()

        for trx in self.transactions:
            if start is not None:
                # If date < start, outside scope.  Skip
                if trx.date < start:
                    continue
            if stop is not None:
                # If date > stop, outside scope.  Skip
                if trx.date > stop:
                    continue
            # If I get here, we're in scope!
            if trx_as_copy:
                trx = copy.deepcopy(trx)
            newtrxs.add_transaction(trx)

        return newtrxs

    def to_csv(self, csv_file, header=True, data_map=None):
        """
        Export transactions in a Transactions instance to a csv file, optionally with a header.

        :param csv_file: Filename to export
        :param header: Boolean to set whether the header is included
        :param data_map: Dictionary that maps data fields to columns in the output file (NOT IMPLEMENTED)
        :return: None
        """
        # TODO: Revisit this with the Transactions as DataFrame.  Reenable test_to_csv
        # FEATURE: Make header let user reorganize and selectively choose what to export?  Use data_map dict?
        if data_map is None:
            # Use default data map from Transaction class if not specified here
            data_map = Transaction.DEFAULT_DATA_MAP
        else:
            raise NotImplementedError("Transactions.to_csv data_map argument not yet implemented")
        attrs = [None] * len(data_map)
        for k, col in data_map.items():
            attrs[col] = k

        with open(csv_file, 'w') as fout:
            if header:
                # Write the header
                fout.write(Transaction.header() + "\n")

            # Write the data
            for trx in self.transactions:
                fout.write(trx.to_csv() + "\n")

    @classmethod
    def from_csv(cls, csv_file, header=True):
        """
        Load a set of transactions from a csv file and return as a Transactions instance.

        :param csv_file: Filename of the csv file to read transactions from
        :param header: If true, first row is taken as a csv header.  The labels in the header will be used to build the
                       fields list passed to the Transaction constructor.
        :return: An instance of Transactions
        """
        with open(csv_file, 'r') as fin:
            csv_list = fin.readlines()
        if header:
            header_text = csv_list.pop(0)
            if not header_text.strip():
                raise ValueError(
                    f"Invalid header in file {csv_file} - header should have 1 or more elements.  " +
                    "Header must be on the first line - check the csv file an empty first line.")
            fields = [text.strip() for text in header_text.split(',')]
        else:
            fields = None

        trxs = Transactions()

        # Loop through all transactions, adding to trxs as we go
        for csv in csv_list:
            # Check for empty lines
            if not csv.strip():
                continue
            trxs.add_transaction(Transaction.from_csv(csv, fields = fields))

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