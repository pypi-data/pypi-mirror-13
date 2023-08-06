from keybin_client.keybin import Keybin
from keybin_client.errors import (KeybinError, AuthenticationError,
                                  NotFoundError, ServerError)


init = Keybin.configure

get_token = Keybin.get_token
list_keys = Keybin.get_keys
get_key_value = Keybin.get_value_for_key
store_key_value = Keybin.store_value_for_key
