import hashlib
import collections


def BuildGatewayToken(options, secret, submit_url, hash_algorithm):
    ordered_params = [
        'account_id',
        'address',
        'amount',
        'bank_code',
        'card_brand',
        'channel',
        'city',
        'country',
        'currency',
        'description',
        'email',
        'emi',
        'mode',
        'name',
        'page_id',
        'payment_mode',
        'payment_option',
        'phone',
        'postal_code',
        'reference_no',
        'return_url',
        'ship_address',
        'ship_city',
        'ship_country',
        'ship_name',
        'ship_phone',
        'ship_postal_code',
        'ship_state',
        'state'
        ]

    ordered_dict = collections.OrderedDict()
    for key in ordered_params:
        ordered_dict[key] = options[key]

    if secret is None or submit_url is None or hash_algorithm is None:
      raise Exception('secret / submit url not found !')

    digest = secret
    for (key, value) in ordered_dict.iteritems():
      if value != None and value != '':
          value = '|' + value
          digest = digest + value

    if hash_algorithm == "md5":
      md5_digest = hashlib.md5(digest.encode())
      hexcode = md5_digest.hexdigest()
    elif hash_algorithm == "sha1":
      md5_digest = hashlib.sha1(digest.encode())
      hexcode = md5_digest.hexdigest()
    elif hash_algorithm == "sha512":
      md5_digest = hashlib.sha512(digest.encode())
      hexcode = md5_digest.hexdigest()
    else:
      raise Exception('No matching algorithms found')


    return hexcode.upper()
