from unittest import TestCase
from Transactions import Transactions
from Transaction import Transaction
import datetime
import copy

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
        for i in range(1, 11):
            trxs = Transactions.sample_trxs(i)
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
        trxs = Transactions.sample_trxs(10)

        temp_outfile = "test_transactions_to_csv.csv"
        trxs.to_csv(temp_outfile)

        # Load csv back as new transactions file
        trxs_loaded = trxs.from_csv(temp_outfile)
        for i in range(len(trxs)):
            self.assertEqual(trxs.transactions[i], trxs_loaded.transactions[i])

    def test_compare(self):
        """
        Test Transactions.__eq__()
        """
        trxs = Transactions.sample_trxs(10)

        # Should be equal to itself
        self.assertEqual(trxs, trxs)

        # Should be equal to something made from all the same transactions
        trxs_fake_copy = Transactions()
        for trx in trxs.transactions:
            trxs_fake_copy.add_transaction(trx)
        self.assertEqual(trxs, trxs_fake_copy)

        # Should be equal to a shallow copy
        trxs_copy = copy.copy(trxs)
        self.assertEqual(trxs, trxs_copy)

        # Even after we change something
        trxs_copy.transactions[0].amount += 1
        self.assertEqual(trxs, trxs_copy)

        # Should be equal to a deep copy
        trxs_deepcopy = copy.deepcopy(trxs)
        self.assertEqual(trxs, trxs_deepcopy)

        # Shouldn't be equal if I change something about the deepcopy
        trxs_deepcopy.transactions[0].amount += 1
        self.assertNotEqual(trxs, trxs_deepcopy)

    def test_slice_by_date(self):
        """
        Test Transactions.slice_by_date by slicing a sample Transactions object
        """
        # Make transactions, one for each month.
        year = 2017
        day = 1
        trx_list = [Transaction.sample_trx(date = datetime.datetime(year, m, day)) for m in range(1,13)]

        trxs = Transactions()
        for trx in trx_list:
            trxs.add_transaction(trx)

        cases = [
            {'start': 4, 'end': 9},
            {'start': None, 'end': 9},
            {'start': 4, 'end': None},
            {'start': None, 'end': None},
        ]

        for case in cases:
            print("Checking case: ", case)
            s = case['start']
            e = case['end']

            if s == None:
                s = 1
                s_datetime = None
            else:
                s = case['start']
                s_datetime = datetime.datetime(year, s, day)

            if e == None:
                e = 12
                e_datetime = None
            else:
                e = case['end']
                e_datetime = datetime.datetime(year, e, day)

            # Make a "reference" trxs that contains what I expect to be in the slice
            trxs_ref = Transactions()
            # Grab everything from s to e, inclusive, recalling that trx_list has month 1 (January) at index 0
            for i in range(s, e+1):
                trxs_ref.add_transaction(trx_list[i-1])

            # Make a slice
            trxs_slice = trxs.slice_by_date(s_datetime, e_datetime)

            # Check
            print("trxs_ref: ")
            print(trxs_ref)
            print("trxs_slice: ")
            print(trxs_slice)
            self.assertEqual(trxs_ref, trxs_slice, msg='Failed on case: {0}'.format(str(case)))

        # Test if slice is a copy of all Transactions
        trxs_slice = trxs.slice_by_date(None, None, trx_as_copy=True)
        trxs_slice.transactions[0].amount += 1
        self.assertNotEqual(trxs, trxs_slice)

        # Test if slice is a view of all Transactions
        trxs_slice = trxs.slice_by_date(None, None, trx_as_copy=False)
        trxs_slice.transactions[0].amount += 1
        self.assertEqual(trxs, trxs_slice)

        start = datetime.datetime.today()
        end = start - datetime.timedelta(1)
        self.assertRaises(ValueError, trxs.slice_by_date, start, end)
