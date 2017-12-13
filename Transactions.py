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

    @classmethod
    def from_csv(cls, csv_file, header = True):
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
            trxs.add_transaction(Transaction.from_csv(csv, data_map=data_map))

        return trxs