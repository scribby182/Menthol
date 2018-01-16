from unittest import TestCase
from Budgets import Budgets
from Budget import Budget
from Transactions import Transactions
from pprint import pprint
import numpy as np

class TestBudgets(TestCase):
    def test_get_transactions_in_budgets(self):
        """
        Test get_transactions_in_budget and get_transactions_not_in_budget
        :return: None
        """
        trxs = Transactions.from_csv('sample_transactions_1.csv')
        budgets_one = Budgets()
        budgets_one.add_budget(Budget(-1, ['One Trx'], name='One Trx Budget'))
        trxs_slice = budgets_one.get_transactions_in_budgets(trxs)
        self.assertEqual(len(trxs_slice), 12)
        trxs_slice = budgets_one.get_transactions_not_in_budgets(trxs)
        self.assertEqual(len(trxs_slice), 24)

        budgets_two = Budgets()
        budgets_two.add_budget(Budget(-2, ['Two Trx'], name='Two Trx Budget'))
        trxs_slice = budgets_two.get_transactions_in_budgets(trxs)
        self.assertEqual(len(trxs_slice), 24)
        trxs_slice = budgets_two.get_transactions_not_in_budgets(trxs)
        self.assertEqual(len(trxs_slice), 12)

        budgets_all = Budgets()
        budgets_all.add_budget(Budget(-1, ['One Trx'], name='One Trx Budget'))
        budgets_all.add_budget(Budget(-2, ['Two Trx'], name='Two Trx Budget'))
        trxs_slice = budgets_all.get_transactions_in_budgets(trxs)
        self.assertEqual(len(trxs_slice), 36)
        trxs_slice = budgets_all.get_transactions_not_in_budgets(trxs)
        self.assertEqual(len(trxs_slice), 0)

        budgets_none = Budgets()
        trxs_slice = budgets_none.get_transactions_in_budgets(trxs)
        self.assertEqual(len(trxs_slice), 0)
        trxs_slice = budgets_none.get_transactions_not_in_budgets(trxs)
        self.assertEqual(len(trxs_slice), 36)

    def test_to_df(self):
        """
        MANUAL TEST - NOT REAL
        :return:
        """
        trxs = Transactions.from_csv('sample_transactions_1.csv')
        budgets_all = Budgets()
        budgets_all.add_budget(Budget(-1, ['One Trx'], name='One Trx Budget'))
        budgets_all.add_budget(Budget(-2, ['Two Trx'], name='Two Trx Budget'))

        reference = np.array([
            [1.,1.0/3.0,2.,1.,3.,2.,4.,3.,5.,4.,6.,5.,7.,6.,8.,7.,9.,8.,10.,9.,11.,10.,12.,11.],
            [1., 1.0 / 3.0, 2., 1., 3., 2., 4., 3., 5., 4., 6., 5., 7., 6., 8., 7., 9., 8., 10., 9., 11., 10., 12.,11.],
        ])
        reference[1,:] *= -2.0

        pprint(reference)


        df = budgets_all.to_df(trxs, moving_average=[1, 3], return_relative=False)
        pprint(df)
        pprint(df.as_matrix())
        pprint(np.all([reference, df.as_matrix()]))
        print(reference - df.as_matrix())
        self.assertTrue(np.all(np.equal(reference, df.as_matrix())))