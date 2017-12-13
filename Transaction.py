import datetime

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
        self.date = None
        self.description = None
        self.description_original = None
        self.amount = None
        self.transaction_type = None
        self.category = None
        self.account = None
        self.labels = None
        self.notes = None

        self.default_data_map =     {
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

        # Parse and reformat results before storing
        # Date
        csv_list[data_map['date']] = datetime.datetime.strptime(csv_list[data_map['date']], TRANSACTION_DATE_FORMAT)
        # Amount
        csv_list[data_map['amount']] = float(csv_list[data_map['amount']])

        # Store attributes in proper spots
        for attr, col in data_map.items():
                setattr(trx, attr, csv_list[col])

        return trx
