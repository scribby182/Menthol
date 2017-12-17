from unittest import TestCase
from Transactions import Transactions
from Transactions import monthdelta
from Transaction import Transaction
import datetime
import copy
import random
import pandas as pd
import numpy as np
import calendar

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
        len_orig = len(trxs)
        trxs.add_transaction(trx)
        print("got trxs: ")
        print(trxs.df)

        self.assertEqual(len(trxs), len_orig + 1, msg='Failed test if add_transaction increases length of trxs.transactions')

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
                "./test_transactions_sample_transactions_with_spaces.csv",
                "./test_transactions_sample_transactions_no_ending_space.csv",
            ]

        for sample_csv in sample_csvs:
            print(f"testing {sample_csv}")
            with open(sample_csv, 'r') as fin:
                sample_csv_list = fin.readlines()

            # Remove Header
            sample_csv_list.pop(0)
            # Remove empty lines
            sample_csv_list = [x for x in sample_csv_list if x.strip()]
            sample_csv_len = len(sample_csv_list)

            trxs = Transactions.from_csv(sample_csv)
            print(trxs)
            self.assertEqual(len(trxs), sample_csv_len, msg="Test failed for {0}".format(sample_csv))


        # Special cases - see if they match trxs from above
        # Transactions with date as final column
        fname = 'test_transactions_sample_transactions_misordered.csv'
        trxs2 = Transactions.from_csv(fname)
        self.assertEqual(trxs, trxs2, msg=f"Test failed for {fname}")

        fname = "./test_transactions_sample_transactions_empty.csv",
        self.assertRaises(ValueError, lambda: Transactions.from_csv(fname))

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
            self.assertEqual(trxs, trxs_loaded)

    def test_compare(self):
        """
        Test Transactions.__eq__()
        """
        trxs_list = [Transaction.sample_trx() for i in range(10)]
        trxs1 = Transactions()
        trxs2 = Transactions()

        for trx in trxs_list:
            trxs1.add_transaction(trx)
            trxs2.add_transaction(trx)

        # Should be equal to itself
        self.assertEqual(trxs1, trxs1)

        # Should be equal to something made from all the same transactions
        self.assertEqual(trxs1, trxs2)

        # Should be equal to a shallow copy
        trxs1_copy = copy.copy(trxs1)
        self.assertEqual(trxs1, trxs1_copy)

        # Even after we change something
        trxs1_copy.df.iloc[0].amount += 1
        self.assertEqual(trxs1, trxs1_copy)

        # Should be equal to a deep copy
        trxs1_deepcopy = copy.deepcopy(trxs1)
        self.assertEqual(trxs1, trxs1_deepcopy)
        # Shouldn't be equal if I change something about the deepcopy
        # Need to use the columns == 'amount' method because iloc doesn't accept columns by name (just a boolean list)
        # and chaining with .amount would cause me to edit a copy, not a view.
        trxs1_deepcopy.df.iloc[0, trxs1_deepcopy.df.columns == 'amount'] = trxs1_deepcopy.df.iloc[0].amount + 1 # Add 1 to all amount fields
        self.assertNotEqual(trxs1, trxs1_deepcopy)

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
                print('adding i: ', i)
                trxs_ref.add_transaction(trx_list[i-1])

            # Make a slice
            trxs_slice = trxs.slice_by_date(s_datetime, e_datetime)

            # Check
            print("trxs_ref: ")
            print(trxs_ref)
            print("trxs_slice: ")
            print(trxs_slice)
            # Reindex the slice's index so they both start at 0...
            trxs_slice.df = trxs_slice.df.reset_index(drop = True)
            self.assertEqual(trxs_ref, trxs_slice, msg='Failed on case: {0}'.format(str(case)))

        # Test if slice is a copy of all Transactions
        trxs_slice = trxs.slice_by_date(None, None)
        trxs_slice.df.iloc[0, trxs_slice.df.columns == 'amount'] += 1
        self.assertNotEqual(trxs, trxs_slice)

        # # Test if slice is a view of all Transactions
        # trxs_slice = trxs.slice_by_date(None, None, trx_as_copy=False)
        # trxs_slice.transactions[0].amount += 1
        # self.assertEqual(trxs, trxs_slice)

        # Check if misordered dates raise ValueError
        start = datetime.datetime.today()
        end = start - datetime.timedelta(1)
        self.assertRaises(ValueError, trxs.slice_by_date, start, end)

    def test_slice_by_categories(self):
        """
            Test Transactions.slice_by_date by slicing a sample Transactions object
        :return:
        """
        trxs = {
            'all': Transactions(),
            'A': Transactions(),
            'B': Transactions(),
            'AB': Transactions(),
        }

        categories = random.choices("ABC", k=10)
        print(categories)
        trx_list = [Transaction.sample_trx(category = categories[i], amount=i) for i in range(len(categories))]

        for trx in trx_list:
            trxs['all'].add_transaction(trx)
            if trx.category == 'A':
                trxs['A'].add_transaction(trx)
                trxs['AB'].add_transaction(trx)
            if trx.category == 'B':
                trxs['B'].add_transaction(trx)
                trxs['AB'].add_transaction(trx)

        for k in trxs:
            print("k: ", k)
            print(trxs[k])

        cases = [
            ['A'],
            ['B'],
            ['A', 'B'],
        ]

        for case in cases:
            print("Checking case: ", case)

            trxs_slice = trxs['all'].slice_by_category(case)
            # Reset index because slice will have different indexing...
            trxs_slice.df = trxs_slice.df.reset_index(drop = True)

            print(trxs_slice)

            if 'A' in case and 'B' in case:
                self.assertNotEqual(trxs['A'], trxs_slice, msg='Failed on case: A compared to {0}'.format(str(case)))
                self.assertNotEqual(trxs['B'], trxs_slice, msg='Failed on case: B compared to {0}'.format(str(case)))
                self.assertEqual(trxs['AB'], trxs_slice, msg='Failed on case: AB compared to {0}'.format(str(case)))
            elif 'A' in case:
                self.assertEqual(trxs['A'], trxs_slice, msg='Failed on case: A compared to {0}'.format(str(case)))
                self.assertNotEqual(trxs['B'], trxs_slice, msg='Failed on case: B compared to {0}'.format(str(case)))
                self.assertNotEqual(trxs['AB'], trxs_slice, msg='Failed on case: AB compared to {0}'.format(str(case)))
            elif 'B' in case:
                self.assertNotEqual(trxs['A'], trxs_slice, msg='Failed on case: A compared to {0}'.format(str(case)))
                self.assertEqual(trxs['B'], trxs_slice, msg='Failed on case: B compared to {0}'.format(str(case)))
                self.assertNotEqual(trxs['AB'], trxs_slice, msg='Failed on case: AB compared to {0}'.format(str(case)))

    def test_summarize_transactions(self):
        """
        Test summarize_transactions
        """
        trxs_list = []
        year = 2016
        dates = [datetime.datetime(year, m, d) for m in range(1,13) for d in [1, 15]]
        print('dates: ')
        print(dates)

        trxs_list.extend([Transaction.sample_trx(date=date, transaction_type='debit', amount=1, category='constant 1') for date in dates])
        trxs_list.extend([Transaction.sample_trx(date=date, transaction_type='debit', amount=i+1, category='linear increasing 1') for i, date in enumerate(dates)])

        y1 = [-2.0] * 12

        y2 = [-(3 + (i-1) * 4) for i in range(1, 13)]
        data = np.array([y1, y2]).T
        dates_1_month = [datetime.datetime(year, m, calendar.monthrange(year, m)[1]) for m in range(1,13)]
        summary_1_ref = pd.DataFrame(data, columns=['constant 1', 'linear increasing 1'], index=dates_1_month)

        y2 = [-(7 + (i-3) * 4) for i in range(3, 13)]
        data = np.array([y1[2:], y2]).T
        dates_3_month = [datetime.datetime(year, m, calendar.monthrange(year, m)[1]) for m in range(3,13)]
        summary_3_ref = pd.DataFrame(data, columns=['constant 1', 'linear increasing 1'], index=dates_3_month)

        y1_partial = [-2/3, -4/3] + y1[2:]
        y2 = [-1, -10/3] + y2
        data = np.array([y1_partial, y2]).T
        dates_3_month = [datetime.datetime(year, m, calendar.monthrange(year, m)[1]) for m in range(1,13)]
        summary_3_ref_partials = pd.DataFrame(data, columns=['constant 1', 'linear increasing 1'], index=dates_3_month)

        trxs = Transactions()
        for trx in trxs_list:
            trxs.add_transaction(trx)

        summary = trxs.summarize_transactions(n_months=1)
        self.assertTrue(summary.equals(summary_1_ref))

        summary = trxs.summarize_transactions(n_months=3)
        self.assertTrue(summary.equals(summary_3_ref))

        summary = trxs.summarize_transactions(n_months=3, start=monthdelta(trxs.df['date'].min(), -2, 1))
        self.assertTrue(summary.equals(summary_3_ref_partials))
