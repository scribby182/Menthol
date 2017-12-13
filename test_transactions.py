from unittest import TestCase
from Transactions import Transactions
from Transaction import Transaction

def make_trx():
    """
    Helper function to make a transaction for testing (there should be better ways to do this...)
    I should probably have something like this in test_Transaction and import it here?
    :return:
    """
    csv = ",".join(["12/11/2017",
                     "Some Transaction Description",
                     "Some Transaction Description Original with Fancy Chars (*&*^*%&^!@#",
                     "20.50",
                     "debit",
                     "Groceries",
                     "Barclaycard",
                     "labels",
                     "some notes with stuff 91287312987393 17239812(@*&#!(*&#(!@#@#%&(!*&#"])
    trx = Transaction.from_csv(csv)
    return trx

class TestTransactions(TestCase):
    """
    Test code for the Transactions class
    """
    def test_add_transaction(self):
        """
        Test code for the add_transaction feature of Transactions class
        """
        trx = make_trx()
        trxs = Transactions()
        len_orig = len(trxs.transactions)
        trxs.add_transaction(trx)

        self.assertEqual(len(trxs.transactions), len_orig + 1, msg='Failed test if add_transaction increases length of trxs.transactions')
        self.assertTrue(isinstance(trxs.transactions[0], Transaction), msg='Failed test if add_transaction yields a Transaction instance in trxs')

    def test_len(self):
        """
        Test Transactions.__len__
        """
        trxs = Transactions()

        for i in range(1, 11):
            trxs.add_transaction(make_trx())
            self.assertEqual(len(trxs), i)