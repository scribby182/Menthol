from unittest import TestCase
from Transaction import Transaction

class TestTransaction(TestCase):
    def test_from_csv(self):
        some_data = ["12/11/2017",
                     "Some Transaction Description",
                     "Some Transaction Description Original with Fancy Chars (*&*^*%&^!@#",
                     "20.50",
                     "debit",
                     "Groceries",
                     "Barclaycard",
                     "labels",
                     "some notes with stuff 91287312987393 17239812(@*&#!(*&#(!@#@#%&(!*&#"]

        # This seems like a dumb way to test this.  What is better?
        # I don't want to just write straight to the attributes
        trx_ref = Transaction.from_csv(some_data)



        trx_jumbled = Transaction

        ordered_csv_string = ",".join(some_data)
        trx = Transaction.from_csv()
        self.assertEqual(1,1)
        # self.fail()
#
# if __name__ == "__main__":
#     unittest.main()