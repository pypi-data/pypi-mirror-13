"""signal request data."""


class SignalRequestData(object):
    """SignalRequestData - map flat formatted structure to nested structure.

    Class to map for instance posted form data to a nested dictionary
    structure. This can be done when fields are named using a convention like:
    name1_name2_name3, but also: name1.name2.name3 .

    Example::

      sarArgs = {
        "customer_email": "test-address@postcode.nl",
        "customer_phoneNumber": "+31235325689",
        "customer_address_postcode": "2012ES",
        "customer_address_houseNumber": "30",
        "customer_address_country": "NL",
        "transaction_internalId": "MyID-249084",
        "transaction_deliveryAddress_postcode": "7514BP",
        "transaction_deliveryAddress_houseNumber": "129",
        "transaction_deliveryAddress_houseNumberAddition": "B",
        "transaction_deliveryAddress_country": "NL"
       }

    with::

       print(json.dumps(SignalRequestData(sarArgs)(),
             sort_keys=True, indent=2))

    will be mapped to::

       {
          "customer": {
            "address": {
              "country": "NL",
              "houseNumber": "30",
              "postcode": "2012ES"
            },
            "email": "test-address@postcode.nl",
            "phoneNumber": "+31235325689"
          },
          "transaction": {
            "deliveryAddress": {
              "country": "NL",
              "houseNumber": "129",
              "houseNumberAddition": "B",
              "postcode": "7514BP"
            },
            "internalId": "MyID-249084"
          }
        }

    """

    def __init__(self, _d=None, delimiter=None):
        """Instantiate a SignalRequestData object.

        Parameters
        ----------
        d : (dict) optional
        """
        self.__structDict = {}
        self.__delim = "_"

        if delimiter:
            self.__delim = delimiter

        if _d:
            [self._transform({k: v}) for (k, v) in _d.items()]

    def _updateItem(self, _dict, keyList, value):
        """_updateItem - private method to construct the dictionary.

        recursively process the keyList to build the structure and assign the
        value

        Parameters
        ----------
        _dict : (dict)

        keyList : (array)
           array of keys to cunstruct the result dictionary

        value : data
           data to assign to the final key that can be identified
           by all keys together, example:

           "customer.address.country" : "NL"

               becomes:

           {
              "customer": {
                "address": {
                  "country": "NL",
               ...
           }
        """
        if len(keyList) == 1:
            _dict.update({keyList[0]: value})
        else:
            if keyList[0] not in _dict:
                _dict.update({keyList[0]: dict()})
            self._updateItem(_dict[keyList[0]], keyList[1:], value)

    def _transform(self, s):
        """_transform - transform a flat formatted key into a structured key.

        Parameters
        ----------
        s : (dict)
        """
        (key, value), = s.items()
        keyList = key.split(self.__delim)
        self._updateItem(self.__structDict, keyList, value)

    def __call__(self):
        """call - return the generated dictionary."""
        return self.__structDict

if __name__ == "__main__":
    import json
    sarArgs = {
            "customer_email": "test-address@postcode.nl",
            "customer_phoneNumber": "+31235325689",
            "customer_address_postcode": "2012ES",
            "customer_address_houseNumber": "30",
            "customer_address_country": "NL",
            "transaction_internalId": "MyID-249084",
            "transaction_deliveryAddress_postcode": "7514BP",
            "transaction_deliveryAddress_houseNumber": "129",
            "transaction_deliveryAddress_houseNumberAddition": "B",
            "transaction_deliveryAddress_country": "NL"
    }
    sarArgs1 = {
            "customer.email": "test-address@postcode.nl",
            "customer.phoneNumber": "+31235325689",
            "customer.address.postcode": "2012ES",
            "customer.address.houseNumber": "30",
            "customer.address.country": "NL",
            "transaction.internalId": "MyID-249084",
            "transaction.deliveryAddress.postcode": "7514BP",
            "transaction.deliveryAddress.houseNumber": "129",
            "transaction.deliveryAddress.houseNumberAddition": "B",
            "transaction.deliveryAddress.country": "NL"
    }
    x = SignalRequestData(sarArgs)()
    print(json.dumps(x, sort_keys=True, indent=2))

    print("--------------------------\n")
    y = SignalRequestData(sarArgs1, delimiter=".")()
    print(json.dumps(y, sort_keys=True, indent=2))
