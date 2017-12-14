from Transaction import Transaction


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

    def add_transaction(self, trx):
        """
        Setter to add a transaction to the object.

        :param trx: An instance of Transaction
        :return: None
        """
        # FEATURE: Auto-sort transactions on add?  Or keep different sorted maps (by category, date, ...)?
        if not isinstance(trx, Transaction):
            raise TypeError("Invalid type for trx ('{0}').  Must be instance of Transaction".format(type(trx)))
        self.transactions.append(trx)

    def to_csv(self, csv_file, header=True, data_map=None):
        """
        Export transactions in a Transactions instance to a csv file, optionally with a header.

        :param csv_file: Filename to export
        :param header: Boolean to set whether the header is included
        :param data_map: Dictionary that maps data fields to columns in the output file (NOT IMPLEMENTED)
        :return: None
        """
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
                       data_map dictionary to construct the transactions.
        :return: An instance of Transactions
        """
        with open(csv_file, 'r') as fin:
            csv_list = fin.readlines()
        if header:
            header = [text.strip() for text in csv_list.pop(0).split(',')]
            data_map = {header[i]: i for i in range(len(header))}
        else:
            data_map = None

        trxs = Transactions()

        # Loop through all transactions, adding to trxs as we go
        for csv in csv_list:
            # Check for empty lines
            if not csv.strip():
                continue
            trxs.add_transaction(Transaction.from_csv(csv, data_map=data_map))

        return trxs
