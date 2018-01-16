import numpy as np
from unittest import TestCase
from Transactions import Transactions, monthdelta
from Budget import Budget


class TestBudget(TestCase):
    def test_to_ds(self):
        """
        Test Budget.to_ds()
        :return: None
        """
        # Simple spot testing
        trxs = Transactions.from_csv('sample_transactions_1.csv')
        # dates = trxs.get_daterange()

        reference = {
            "One": np.array([1.,1.0/3.0,2.,1.,3.,2.,4.,3.,5.,4.,6.,5.,7.,6.,8.,7.,9.,8.,10.,9.,11.,10.,12.,11.]),
            "Two": np.array([1., 1.0 / 3.0, 2., 1., 3., 2., 4., 3., 5., 4., 6., 5., 7., 6., 8., 7., 9., 8., 10., 9., 11., 10., 12.,11.]) * -2,
        }

        b_dict = {
            "One": Budget(0, ['One Trx'], name='One Trx Budget'),
            "Two": Budget(0, ['Two Trx'], name='Two Trx Budget'),
        }

        for k in sorted(reference):
            ds =  b_dict[k].to_ds(trxs, moving_average=[1, 3], return_relative=True)
            data = ds.as_matrix()
            self.assertTrue(np.all(np.equal(data, reference[k])), msg=f"Failed test case {k}")
