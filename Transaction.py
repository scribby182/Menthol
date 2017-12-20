import datetime
import random
import string
import pandas as pd
import numpy as np
from collections import OrderedDict


class Transaction(object):
    """
    Class to store a single transaction record.
    """
    MINT_CSV_DATE_FORMAT = "%m/%d/%Y"
    DEFAULT_DATA = np.array(
        [
            ("Date", 'datetime64'),
            ("Description", 'object'),
            ("Description Original", 'object'),
            ("Amount", 'float64'),
            ("Transaction Type", 'object'),
            ("Category", 'object'),
            ("Account", 'object'),
            ("Labels", 'object'),
            ("Notes", 'object'),
        ]
    )

    def __init__(self):
        """
        Initialize an empty Transaction instance.
        """
        self.data = OrderedDict()
        for row in self.DEFAULT_DATA:
            self.data[row[0]] = [row[1], None]

    def __str__(self):
        signed_amount = self.amount
        date = self.date.strftime(self.MINT_CSV_DATE_FORMAT)
        if self.transaction_type == 'debit':
            signed_amount = signed_amount * -1
        ret = f"{date} | {self.description} | {signed_amount} | {self.category} | {self.account}"
        return ret

    def __eq__(self, other):
        """
        Compare self to another object to determine if they are equal.

        :param other: Another object (must be Transaction-like to be equal)
        :return: Boolean of whether the objects are equal
        """
        comparible_attributes = ["Date", "Description", "Description Original", "Amount", "Transaction Type",
                                 "Category", "Account", "Labels", "Notes"]
        equal = True
        for attr in comparible_attributes:
            if getattr(self, attr) == getattr(other, attr):
                continue
            else:
                equal = False
                break
        return equal

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
        print("using defaults:")
        print(defaults)
        return Transaction.from_dict(defaults)

    def header(self, separator=', ', fields=None):
        """
        Returns a csv string in the format of a standard csv header file.

        KeyError will be raised if a key does not exist

        :param keys: Ordered subset of keys to include in the returned string.
        :return: A csv-formatted string
        """
        if fields is None:
            fields = list(self.fields)

        return separator.join(fields)

    def to_list(self, fields=None):
        """
        Returns a list of the data in the Transaction.

        :param fields: (Optional) Defines an ordered list of the fields to return
        :return: List containing date requested
        """
        if fields is None:
            fields = self.fields

        data = [getattr(self, field) for field in fields]
        return data

    def to_csv(self, separator=', ', fields=None):
        """
        Convert the transaction to a csv formatted string.

        KeyError will be raised if a field does not exist in the transaction

        :param field: Ordered subset of fields to export in the returned string.
        :return: A csv-formatted string
        """
        #TODO: Cehck if KeyError raised on incorrect key
        if fields is None:
            fields = self.fields

        trx_as_list = [None] * len(fields)
        for i, field in enumerate(fields):
            trx_as_list[i] = getattr(self, field)
            if field == 'Date':
                trx_as_list[i] = trx_as_list[i].strftime(Transaction.MINT_CSV_DATE_FORMAT)
            if field == 'Amount':
                trx_as_list[i] = str(trx_as_list[i])

        return separator.join(trx_as_list)

    @classmethod
    def from_dict(cls, data_dict, fill_blanks=False):
        """
        Return a Transaction initialized from a dict containing data for all fields in Transaction.DEFAULT_DATA_MAP

        :param data_dict:
        :param fill_blanks: If True, fill all blank fields with None except date and amount, which is always required
        :return:
        """
        trx = cls()
        # if len(data_dict) != len(trx.fields):
        #     raise KeyError("Keys of data_dict ({0}) do not match fields of transaction ({1})".format(str(data_dict.keys()), str(trx.fields)))
        for k in trx.fields:
            try:
                setattr(trx, k, data_dict[k])
            except KeyError as e:
                if fill_blanks:
                    setattr(trx, k, None)
                else:
                    raise KeyError(f"data_dict ({str(data_dict.keys())}) is missing required keys for transaction ({str(trx.fields)})")
        return trx

    @classmethod
    def from_csv(cls, csv_string, separator=',', fields=None):
        """
        Initialize and return a Transaction instance from a comma separated string.

        Data from csv_string will be mapped to transaction fields according to fields input list.

        :param csv_string:
        :param separator: String that separates each value in the string (default: ',')
        :param fields: An ordered list of of the fields in the csv.  If None, default behaviour uses the order specified
                       by the transaction's fields attribute

        :return: A Transaction instance
        """
        trx = cls()
        if fields is None:
            fields = trx.fields

        # Split and strip any extra whitespace
        csv_list = [text.strip() for text in csv_string.split(separator)]

        for i in range(len(csv_list)):
            setattr(trx, fields[i], csv_list[i])

        return trx

    @property
    def date(self):
        """
        Getter for date property.

        :return: Datetime instance
        """
        return self.data['Date'][1]

    @date.setter
    def date(self, value):
        """
        Setter for date property.

        :return: None
        """
        # Parse (If necessary) and store date
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime.strptime(value, Transaction.MINT_CSV_DATE_FORMAT)
        # If we get here, we have a datetime.datetime object
        self.data['Date'][1] = value  # No need to make a copy - datetime objects are immutable

    @property
    def amount(self):
        """
        Getter for amount property.

        :return: float
        """
        return self.data['Amount'][1]

    @amount.setter
    def amount(self, value):
        """
        Setter for amount property.

        :return: None
        """
        self.data['Amount'][1] = round(float(value), 2)

    @property
    def signed_amount(self):
        """
        Getter for amount with a +/- sign
        :return:
        """
        signed_amount = self.amount
        if self.transaction_type == 'debit':
            signed_amount = signed_amount * -1
        return signed_amount
    # # Not sure if I want to change the setting behaviour here... seems a little confusing and for little real gain
    # @signed_amount.setter
    # def signed_amount(self, value):
    #     """
    #     Setter for the property signed_amount, which automatically sets transaction_type accordingly
    #     :param value:
    #     :return:
    #     """
    #     if value >= 0:
    #         self.transaction_type = 'credit'
    #         self.amount = value
    #     else:
    #         self.transaction_type = 'debit'
    #         self.amount = -value

    @property
    def description(self):
        """
        Getter for property description, accessing data from internal Pandas Series
        """
        return self.data['Description'][1]

    @description.setter
    def description(self, value):
        """
        Setter for description property.

        :param value:
        :return:
        """
        self.data['Description'][1] = value

    @property
    def description_original(self):
        """
        Getter for property description_original, accessing data from internal Pandas Series
        """
        return self.data['Description Original'][1]

    @description_original.setter
    def description_original(self, value):
        """
        Setter for description_original property.

        :param value:
        :return:
        """
        self.data['Description Original'][1] = value

    @property
    def transaction_type(self):
        """
        Getter for property transaction_type, accessing data from internal Pandas Series
        """
        return self.data['Transaction Type'][1]

    @transaction_type.setter
    def transaction_type(self, value):
        """
        Setter for transaction_type property.

        :param value:
        :return:
        """
        self.data['Transaction Type'][1] = value

    @property
    def category(self):
        """
        Getter for property category, accessing data from internal Pandas Series
        """
        return self.data['Category'][1]

    @category.setter
    def category(self, value):
        """
        Setter for category property.

        :param value:
        :return:
        """
        self.data['Category'][1] = value

    @property
    def account(self):
        """
        Getter for property account, accessing data from internal Pandas Series
        """
        return self.data['Account'][1]

    @account.setter
    def account(self, value):
        """
        Setter for account property.

        :param value:
        :return:
        """
        self.data['Account'][1] = value

    @property
    def labels(self):
        """
        Getter for property labels, accessing data from internal Pandas Series
        """
        return self.data['Labels'][1]

    @labels.setter
    def labels(self, value):
        """
        Setter for labels property.

        :param value:
        :return:
        """
        self.data['Labels'][1] = value

    @property
    def notes(self):
        """
        Getter for property notes, accessing data from internal Pandas Series
        """
        return self.data['Notes'][1]

    @notes.setter
    def notes(self, value):
        """
        Setter for notes property.

        :param value:
        :return:
        """
        self.data['Notes'][1] = value

    @property
    def fields(self):
        """
        Getter for property notes, accessing data from internal Pandas Series
        """
        return list(self.data.keys())