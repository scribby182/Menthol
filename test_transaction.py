from unittest import TestCase
from Transaction import Transaction
import datetime

class TestTransaction(TestCase):
    def test_from_csv(self):
        """
        Test cases for Transaction.from_csv.

        These could be written in a much better way I think...  This is a first attempt.
        :return:
        """
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
                     25.50,
                     "credit",
                     "Rent",
                     "Amex",
                     "craziness galore!",
                     "No notes here"]

        # Test basic cases with csv in default order
        csv_to_test = {
            'no_spaces': ",".join(some_data),
            'spaces': ',     '.join(some_data),
        }
        for name, csv_string in csv_to_test.items():
            trx = Transaction.from_csv(csv_string)
            for attr, col in data_map.items():
                self.assertEqual(getattr(trx, attr), some_correct_results[col], msg="Failed csv case {0} on attr {1} (match against correct results)".format(name, attr))
                self.assertNotEqual(getattr(trx, attr), some_incorrect_results[col], msg="Failed csv case {0} on attr {1} (negative match against incorrect results)")

        # Test for Misordered data
        misordered_data_map = {
                        "date": 1,
                        "description": 2,
                        "description_original": 3,
                        "amount": 4,
                        "transaction_type": 5,
                        "category": 6,
                        "account": 7,
                        "labels": 8,
                        "notes": 0,
                    }
        some_misordered_data = [None] * len(some_data)
        some_misordered_correct_results = [None] * len(some_misordered_data)
        for attr, col_ordered in data_map.items():
            col_misordered = misordered_data_map[attr]
            some_misordered_data[col_misordered] = some_data[col_ordered]
            some_misordered_correct_results[col_misordered] = some_correct_results[col_ordered]
        misordered_csv = ",".join(some_misordered_data)
        print('misordered: ')
        print(misordered_csv)
        trx = Transaction.from_csv(misordered_csv, misordered_data_map)
        for attr, col in misordered_data_map.items():
            print("running attr:", attr)
            print("running col:", col)
            self.assertEqual(getattr(trx, attr), some_misordered_correct_results[col],
                             msg="Failed csv case {0} on attr {1} (match against correct results)".format(name, attr))

        some_bad_data = {}
        bad = list(some_data)
        bad[0] = 'not a date'
        some_bad_data['wrong_date_format'] = bad

        for name, data in some_bad_data.items():
            data_csv = ','.join(data)
            self.assertRaises(ValueError, Transaction.from_csv, data_csv)

    def test_from_dict(self):
        """
        Test Transaction.from_dict constructor
        """
        some_data_list = ["12/11/2017",
                     "Some Transaction Description",
                     "Some Transaction Description Original with Fancy Chars (*&*^*%&^!@#",
                     "20.50",
                     "debit",
                     "Groceries",
                     "Barclaycard",
                     "labels",
                     "some notes with stuff 91287312987393 17239812(@*&#!(*&#(!@#@#%&(!*&#"]
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
        some_data_dict = {
                        "date": some_data_list[0],
                        "description": some_data_list[1],
                        "description_original": some_data_list[2],
                        "amount": some_data_list[3],
                        "transaction_type": some_data_list[4],
                        "category": some_data_list[5],
                        "account": some_data_list[6],
                        "labels": some_data_list[7],
                        "notes": some_data_list[8],
                    }

        some_correct_results = [datetime.datetime(2017, 12, 11),
                                "Some Transaction Description",
                                "Some Transaction Description Original with Fancy Chars (*&*^*%&^!@#",
                                20.50,
                                "debit",
                                "Groceries",
                                "Barclaycard",
                                "labels",
                                "some notes with stuff 91287312987393 17239812(@*&#!(*&#(!@#@#%&(!*&#"]

        trx_dict = Transaction.from_dict(some_data_dict)
        trx_csv = Transaction.from_csv(",".join(some_data_list))
        for attr, val in some_data_dict.items():
            self.assertEqual(getattr(trx_dict, attr), some_correct_results[data_map[attr]])
            self.assertEqual(getattr(trx_dict, attr), getattr(trx_csv, attr))

if __name__ == "__main__":
    unittest.main()