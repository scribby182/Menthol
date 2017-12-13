from unittest import TestCase
from Transaction import Transaction
import datetime

class TestTransaction(TestCase):
    def test_from_csv(self):
        data_map = {
                        "date": 0,
                        "description": 1,
                        "description_original": 2,
                        "amount": 3,
                        "transaction_type": 4,
                        "category": 5,
                        "account": 6,
                        "labels": 7,
                        "notes": 8,
                    }

        some_data = ["12/11/2017",
                     "Some Transaction Description",
                     "Some Transaction Description Original with Fancy Chars (*&*^*%&^!@#",
                     "20.50",
                     "debit",
                     "Groceries",
                     "Barclaycard",
                     "labels",
                     "some notes with stuff 91287312987393 17239812(@*&#!(*&#(!@#@#%&(!*&#"]

        some_correct_results = [datetime.datetime(2017, 12, 11),
                     "Some Transaction Description",
                     "Some Transaction Description Original with Fancy Chars (*&*^*%&^!@#",
                     20.50,
                     "debit",
                     "Groceries",
                     "Barclaycard",
                     "labels",
                     "some notes with stuff 91287312987393 17239812(@*&#!(*&#(!@#@#%&(!*&#"]

        some_incorrect_results = [datetime.datetime(2117, 12, 11),
                     "Some Transaction Description111",
                     "Some Transaction Description 111Original with Fancy Chars (*&*^*%&^!@#",
                     "25.50",
                     "credit",
                     "Rent",
                     "Amex",
                     "craziness galore!",
                     "No notes here"]


        # Test basic cases with csv in default order
        csv_to_test = {
            'no_spaces': ",".join(some_data),
            'spaces': ', '.join(some_data),
        }
        for name, csv_string in csv_to_test.items():
            trx = Transaction.from_csv(csv_string)
            for attr, col in data_map.items():
                self.assertEqual(getattr(trx, attr), some_correct_results[col], msg="Failed csv case {0} on attr {1} (match against correct results)".format(name, attr))
                self.assertNotEqual(getattr(trx, attr), some_incorrect_results[col], msg="Failed csv case {0} on attr {1} (negative match against incorrect results)")


if __name__ == "__main__":
    unittest.main()