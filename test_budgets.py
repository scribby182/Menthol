from unittest import TestCase
from Budgets import Budgets
from Budget import Budget
from Transactions import Transactions

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

