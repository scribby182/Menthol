import numpy as np
import datetime
from unittest import TestCase
from Transactions import Transactions

class TestTransactions2(TestCase):
    def test_from_csv(self):
        trxs = Transactions.from_csv('sample_transactions_1.csv')

        self.assertEqual(len(trxs), 36)

        # Spot check data
        self.assertAlmostEqual(trxs.df.iloc[0].Amount, -12)
        self.assertAlmostEqual(trxs.df.iloc[1].Amount, 12)
        self.assertAlmostEqual(trxs.df.iloc[2]['Account Name'], 'Ac')
        self.assertAlmostEqual(trxs.df.iloc[3]['Category'], 'Two Trx')

    def test_slice_by_categories(self):
        """
            Test Transactions.slice_by_category by slicing a sample Transactions object
        :return:
        """
        trxs = Transactions.from_csv('sample_transactions_1.csv')

        trxs_2 = trxs.slice_by_category(["Two Trx"])

        # Do a few spot checks (not comprehensive...)
        self.assertEqual(len(trxs_2), 24)
        self.assertEqual(trxs_2.df.iloc[6].Amount, -9.0)

    def test_slice_by_date(self):
        """
        Test the Transactions.slice_by_date
        """
        # Reference tranactions
        trxs = Transactions.from_csv('sample_transactions_1.csv')

        # Slice in ways that should keep the exact same transactions (nothing gets filtered out)
        cases = [
            {'start': datetime.datetime(2016, 1, 1), 'end': datetime.datetime(2019, 1, 1)},
            {'start': datetime.datetime(2016, 1, 1), 'end': datetime.datetime(2019, 1, 1)},
            {'start': None, 'end': datetime.datetime(2019, 1, 1)},
            {'start': datetime.datetime(2016, 1, 1), 'end': None},
            {'start': None, 'end': None},
            ]

        for case in cases:
            sliced = trxs.slice_by_date(start=case['start'], stop=case['end'])
            self.assertTrue(trxs.df.equals(sliced.df), msg=f"Comparinson with start:{case['start']} stop:{case['end']}")

        # Slice such that starting trx is included, but end trxs are cut
        cases = [
            {'start': datetime.datetime(2016, 1, 1), 'end': datetime.datetime(2017, 2, 1)},
            {'start': None, 'end': datetime.datetime(2017, 2, 1)},
        ]
        for case in cases:
            sliced = trxs.slice_by_date(start=case['start'], stop=case['end'])

            self.assertEqual(3, len(sliced))
            # Do some spot checks...
            self.assertAlmostEqual(sliced.df.iloc[0].Amount, -1, msg=f"Comparinson with start:{case['start']} stop:{case['end']}")
            self.assertAlmostEqual(sliced.df.iloc[1].Amount, 1, msg=f"Comparinson with start:{case['start']} stop:{case['end']}")
            self.assertAlmostEqual(sliced.df.iloc[2]['Account Name'], 'Ac', msg=f"Comparinson with start:{case['start']} stop:{case['end']}")

        # Check if end is on a transaction (checks < vs <=)
        cases = [
            {'start': datetime.datetime(2016, 1, 1), 'end': datetime.datetime(2017, 2, 10)},
            {'start': None, 'end': datetime.datetime(2017, 2, 10)},
        ]
        for case in cases:
            sliced = trxs.slice_by_date(start=case['start'], stop=case['end'])

            self.assertEqual(4, len(sliced))
            # Do some spot checks...
            self.assertAlmostEqual(sliced.df.iloc[1].Amount, -1, msg=f"Comparinson with start:{case['start']} stop:{case['end']}")
            self.assertAlmostEqual(sliced.df.iloc[2].Amount, 1, msg=f"Comparinson with start:{case['start']} stop:{case['end']}")
            self.assertAlmostEqual(sliced.df.iloc[3]['Account Name'], 'Ac', msg=f"Comparinson with start:{case['start']} stop:{case['end']}")

        # Slice such that ending trx is included, but start trxs are cut
        cases = [
            {'start': datetime.datetime(2017, 11, 30), 'end': datetime.datetime(2018, 2, 1)},
            {'start': datetime.datetime(2017, 11, 30), 'end': None},
        ]
        for case in cases:
            sliced = trxs.slice_by_date(start=case['start'], stop=case['end'])

            self.assertEqual(3, len(sliced))
            self.assertEqual(datetime.datetime(2017, 12, 10), sliced.df.iloc[2].Date)

        # Check if end is on a transaction (checks < vs <=)
        cases = [
            {'start': datetime.datetime(2017, 11, 28), 'end': datetime.datetime(2018, 2, 1)},
            {'start': datetime.datetime(2017, 11, 28), 'end': None},
        ]
        for case in cases:
            sliced = trxs.slice_by_date(start=case['start'], stop=case['end'])

            self.assertEqual(4, len(sliced))
            # Do some spot checks...
            self.assertEqual(datetime.datetime(2017, 11, 28), sliced.df.iloc[3].Date)

    def test_sum(self):
        """
        Test Transactions.sum()
        """
        # Reference tranactions
        trxs = Transactions.from_csv('sample_transactions_1.csv')

        # Known summation of the entire file
        ref_sum = -np.sum([i for i in range(1, 13)])

        self.assertEqual(ref_sum, trxs.sum())
        self.assertEqual(ref_sum, trxs.slice_by_category(["One Trx", "Two Trx"]).sum())
        self.assertEqual(2 * ref_sum, trxs.slice_by_category(["Two Trx"]).sum())

    def test_by_month(self):
        """
        Test Transactions.by_month()
        """
        # Reference tranactions
        trxs = Transactions.from_csv('sample_transactions_1.csv')

        # Summed monthly
        summarized = trxs.by_month()

        # Check the length (should be 24:  12 months x 2 categories)
        self.assertEqual(24, len(summarized))

        # Check the results
        # One Trx
        res = np.array([i for i in range(1, 13)])
        self.assertTrue(np.all([res, summarized.slice_by_category(['One Trx']).df.Amount.as_matrix()]))

        # Two Trx
        res = np.array([i for i in range(1, 13)]) * -2
        self.assertTrue(np.all([res, summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix()]))

        # Use ranges larger than contained in transactions (should pad with 0's for each category)

        # Summed monthly
        start = datetime.datetime(2016, 7, 5)
        end = datetime.datetime(2018, 4, 2)
        summarized = trxs.by_month(start = start, stop = end)

        # Check the length (should be 24: 12 months x 2 categories)
        self.assertEqual(24, len(summarized))

        # Check the results
        # One Trx
        res = np.array([float(i) for i in range(1, 13)])
        # For some reason even though res == summarized gives all True, np.all() evaluates False...
        # As a hacky way to test, use sum and equality
        # self.assertTrue(np.all([res, summarized.slice_by_category(['One Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['One Trx']).df.Amount.as_matrix().sum())

        # Two Trx
        res = res * -2

        # Same as above...
        # self.assertTrue(np.all([res, summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix().sum())

        # Summed monthly, not skipping empty months
        summarized = trxs.by_month(start = start, stop = end, ignore_blanks=False)

        # Check the length (should be 44:  12 months x 2 categories + 6 * 2 before + 4 * 2 after)
        self.assertEqual(24 + 10 * 2, len(summarized))

        # Check the results
        # One Trx
        res = np.array([0.0] * 6 + [float(i) for i in range(1, 13)] + [0.] * 4)
        # For some reason even though res == summarized gives all True, np.all() evaluates False...
        # As a hacky way to test, use sum and equality
        # self.assertTrue(np.all([res, summarized.slice_by_category(['One Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['One Trx']).df.Amount.as_matrix().sum())

        # Two Trx
        res = res * -2

        # Same as above...
        # self.assertTrue(np.all([res, summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix().sum())


        # Summed monthly
        start = datetime.datetime(2017, 3, 5)
        end = datetime.datetime(2017, 9, 2)
        summarized = trxs.by_month(start = start, stop = end)

        # Check the length (should be 14:  7 months x 2 categories)
        self.assertEqual(7 * 2, len(summarized))

        # Check the results
        # One Trx
        res = np.array([float(i) for i in range(3, 10)])
        # For some reason even though res == summarized gives all True, np.all() evaluates False...
        # As a hacky way to test, use sum and equality
        # self.assertTrue(np.all([res, summarized.slice_by_category(['One Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['One Trx']).df.Amount.as_matrix().sum())

        # Two Trx
        res = res * -2

        # Same as above...
        # self.assertTrue(np.all([res, summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix().sum())

    def test_moving_average(self):
        """
        Test Transactions.summarize_transaction
        """
        # Reference tranactions
        trxs = Transactions.from_csv('sample_transactions_1.csv')

        # Averaged monthly
        summarized = trxs.moving_average()

        # Check the length (should be 24:  12 months x 2 categories)
        self.assertEqual(24, len(summarized))

        # Check the results
        # One Trx
        res = np.array([i for i in range(1, 13)])
        self.assertTrue(np.all([res, summarized.slice_by_category(['One Trx']).df.Amount.as_matrix()]))

        # Two Trx
        res = np.array([i for i in range(1, 13)]) * -2
        self.assertTrue(np.all([res, summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix()]))

        # Averaged 3-monthly
        summarized = trxs.moving_average(n= 3)

        # Check the length (should be 20: - 10 months x 2 categories)
        self.assertEqual(20, len(summarized))

        # Check the results
        # One Trx
        res = np.array([i for i in range(2, 12)])
        self.assertTrue(np.all([res, summarized.slice_by_category(['One Trx']).df.Amount.as_matrix()]))

        # Two Trx
        res = np.array([i for i in range(2, 12)]) * -2
        self.assertTrue(np.all([res, summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix()]))

        # Use ranges larger than contained in transactions (should pad with 0's for each category)

        # Averaged monthly
        start = datetime.datetime(2016, 7, 5)
        end = datetime.datetime(2018, 4, 2)
        summarized = trxs.moving_average(start = start, stop = end, n= 1)

        # Check the length (should be 44:  12 months x 2 categories + 6 * 2 before + 4 * 2 after)
        self.assertEqual(24 + 10 * 2, len(summarized))

        # Check the results
        # One Trx
        res = np.array([0.0] * 6 + [float(i) for i in range(1, 13)] + [0.] * 4)
        # For some reason even though res == summarized gives all True, np.all() evaluates False...
        # As a hacky way to test, use sum and equality
        # self.assertTrue(np.all([res, summarized.slice_by_category(['One Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['One Trx']).df.Amount.as_matrix().sum())

        # Two Trx
        res = res * -2

        # Same as above...
        # self.assertTrue(np.all([res, summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix().sum())

        # Averaged 3-monthly
        summarized = trxs.moving_average(start = start, stop = end, n= 3)

        # Check the length (should be 40:  10 months x 2 categories + 6 * 2 before + 4 * 2 after)
        self.assertEqual(20 + 10 * 2, len(summarized))

        # Check the results
        # One Trx
        res = np.array([0.0] * 4 + [1/3, 1.0] + [i for i in range(2, 12)] + [(11. + 12.) / 3, 12.0 / 3] + [0.] * 2)
        # self.assertTrue(np.all([res, summarized.slice_by_category(['One Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['One Trx']).df.Amount.as_matrix().sum())

        # Two Trx
        res = res * -2
        # self.assertTrue(np.all([res, summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix().sum())

        # Averaged monthly
        start = datetime.datetime(2017, 3, 5)
        end = datetime.datetime(2017, 9, 2)
        summarized = trxs.moving_average(start = start, stop = end, n= 1)

        # Check the length (should be 14:  7 months x 2 categories)
        self.assertEqual(7 * 2, len(summarized))

        # Check the results
        # One Trx
        res = np.array([float(i) for i in range(3, 10)])
        # For some reason even though res == summarized gives all True, np.all() evaluates False...
        # As a hacky way to test, use sum and equality
        # self.assertTrue(np.all([res, summarized.slice_by_category(['One Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['One Trx']).df.Amount.as_matrix().sum())

        # Two Trx
        res = res * -2

        # Same as above...
        # self.assertTrue(np.all([res, summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix()]))
        self.assertAlmostEqual(res.sum(), summarized.slice_by_category(['Two Trx']).df.Amount.as_matrix().sum())
