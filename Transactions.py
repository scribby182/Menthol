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