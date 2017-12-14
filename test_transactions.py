from unittest import TestCase
from Transactions import Transactions
from Transaction import Transaction

class TestTransactions(TestCase):
    """
    Test code for the Transactions class
    """
    def test_add_transaction(self):
        """
        Test code for the add_transaction feature of Transactions class
        """
        trx = Transaction.sample_trx()
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
            trxs.add_transaction(Transaction.sample_trx())
            self.assertEqual(len(trxs), i)

    def test_from_csv(self):
        """
        Test Transactions.from_csv

        Currently only validates that the method did not raise an exception and resulted in the right number of
        transactions.  Does not validate the content (at least not more than the properties of Transaction do)

        How do I make a test case for something that loads a bunch of stuff that depends on a file?  If I dynamically
        try to predict the result, that is just as flawed as the method I'm testing.  But if I do manual checks, those
        are either incomplete or tedious...
        """
        sample_csvs = \
            [
                "./test_transactions_sample_transactions.csv",
                "./test_transactions_sample_transactions_empty.csv",
                "./test_transactions_sample_transactions_with_spaces.csv",
                "./test_transactions_sample_transactions_no_ending_space.csv",
            ]

        for sample_csv in sample_csvs:
            with open(sample_csv, 'r') as fin:
                sample_csv_list = fin.readlines()

            # Remove Header
            sample_csv_list.pop(0)
            # Remove empty lines
            sample_csv_list = [x for x in sample_csv_list if x.strip()]
            sample_csv_len = len(sample_csv_list)

            trxs = Transactions.from_csv(sample_csv)
            self.assertEqual(len(trxs), sample_csv_len, msg="Test failed for {0}".format(sample_csv))

    def test_to_csv(self):
        """
        Test Transactions.to_csv by creating data, exporting to csv, then reimporting.
        :return:
        """
        trx_list = [Transaction.sample_trx() for i in range(10)]
        trxs = Transactions()
        for trx in trx_list:
            trxs.add_transaction(trx)

        temp_outfile = "test_transactions_to_csv.csv"
        trxs.to_csv(temp_outfile)

        # Load csv back as new transactions file
        trxs_loaded = trxs.from_csv(temp_outfile)
        for i in range(len(trxs)):
            self.assertEqual(trxs.transactions[i], trxs_loaded.transactions[i])