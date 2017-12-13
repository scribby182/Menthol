import datetime
import random
import string

# FEATURE: Add properties of setters/getters for all attributes.  Validate on set (eg: make sure date is a datetime format or can be converted to one, etc.)
# FEATURE: Add Unit Tests

TRANSACTION_DATE_FORMAT = "%m/%d/%Y"

class Transaction(object):
    """
    Class to store a single transaction record.
    """

    def __init__(self):
        """
        Initialize an empty Transaction instance.
        """
        self._date = None
        self.description = None
        self.description_original = None
        self._amount = None
        self.transaction_type = None
        self.category = None
        self.account = None
        self.labels = None
        self.notes = None

        self.default_data_map = {
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

    def __str__(self):
        signed_amount = self.amount
        if self.transaction_type == 'debit':
            signed_amount = signed_amount * -1
        string = "{0} | ${1} | {2} | {3}".format(self.description, signed_amount, self.category, self.account)
        return string

    @classmethod
    def sample_trx(cls, **kwargs):
        """
        Returns a sample transaction with semi-random date.

        Random data can be overridden through input arguemnts

        :return:
        """
        trx_desc = random.choice(string.ascii_uppercase)
        defaults = {
            "date": "{0}/{1}/{2}".format(random.randint(1, 12), random.randint(1, 28), random.randint(1985, 2016)),
            "description": "Trx {0}".format(trx_desc),
            "description_original": "Trx {0} Long".format(trx_desc),
            "amount": random.random() * 100.0,
            "transaction_type": "{0}".format(random.choice(['debit', 'credit'])),
            "category": "{0}".format(random.choice(['Groceries', 'Mortgage'])),
            "account": "{0}".format(random.choice(['Barclay', 'Amex'])),
            "labels": "label1",
            "notes": "A note",
        }
        defaults.update(**kwargs)
        return Transaction.from_dict(defaults)


    @classmethod
    def from_dict(cls, data_dict):
        """
        Initialize and return a transaction from a dictionary specifying all data called for in self.default_data_map

        :param data_dict:
        :return:
        """
        trx = cls()
        for k in trx.default_data_map.keys():
            setattr(trx, k, data_dict[k])
        return trx

    @classmethod
    def from_csv(cls, csv_string, data_map=None):
        """
        Initialize and return a Transaction instance from a comma separated string.

        Data from csv_string will be mapped to internal attributes according to data_map.

        :param csv_string:
        :param data_map: A dictionary mapping Transaction attributes to positions in csv_string by {attr: position}.
                         Default is:
                            {
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

        :return:
        """

        trx = cls()
        if data_map is None:
            data_map = dict(trx.default_data_map)

        # Split and strip any extra whitespace
        csv_list = [text.strip() for text in csv_string.split(',')]

        # Store attributes in proper spots
        for attr, col in data_map.items():
                setattr(trx, attr, csv_list[col])

        return trx

    @property
    def date(self):
        """
        Getter for date property.

        :return: Datetime instance
        """
        return self._date

    @date.setter
    def date(self, value):
        """
        Setter for date property.

        :return: None
        """
        # Parse (If necessary) and store date
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime.strptime(value, TRANSACTION_DATE_FORMAT)
        # If we get here, we have a datetime.datetime object
        self._date = value  # No need to make a copy - datetime objects are immutable

    @property
    def amount(self):
        """
        Getter for amount property.

        :return: float
        """
        return self._amount


    @amount.setter
    def amount(self, value):
        """
        Setter for amount property.

        :return: None
        """
        self._amount = round(float(value), 2)
