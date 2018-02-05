import os

from notebook.base.handlers import IPythonHandler
import pizzapi

REQUIRED_ENV_VARS = [
    "FIRST_NAME",
    "LAST_NAME",
    "EMAIL",
    "PHONE",
    "STREET",
    "CITY",
    "REGION",
    "DELIVERY_ZIP",
    "CC_NUMBER",
    "EXPIRATION",
    "CVV",
    "BILLING_ZIP",
    "MY_ORDER_ITEMS"
]


def _find_missing_env():
    missing = []
    for env_var in REQUIRED_ENV_VARS:
        if env_var not in os.environ:
            missing.append(env_var)
    return missing


def _display_missing(missing):
    if len(missing) > 0:
        print("The following environment variables are missing:")
        print(missing)
        print("export them in your terminal before continuing")
    else:
        print("All required variables are present!")


def check_env():
    missing = _find_missing_env()
    _display_missing(missing)


def _check_exit_code(retcode, err_msg):
    if retcode != 0:
        raise AssertionError(err_msg)


def _check_defined(env_var, err_msg):
    if env_var not in os.environ:
        raise AssertionError(err_msg.format(env_var))


def build_customer():
    for env_var in ['FIRST_NAME', 'LAST_NAME', 'EMAIL', 'PHONE']:
        _check_defined(env_var, "Required Customer Env Var {} is not defined!")
    e = os.environ
    return pizzapi.Customer(fname=e['FIRST_NAME'],
                            lname=e['LAST_NAME'],
                            email=e['EMAIL'],
                            phone=e['PHONE'])


def build_address():
    for env_var in ['STREET', 'CITY', 'REGION', 'DELIVERY_ZIP']:
        _check_defined(env_var, "Required Address Env Var {} is not defined!")
    e = os.environ
    return pizzapi.Address(street=e['STREET'],
                           city=e['CITY'],
                           region=e['REGION'],
                           zip=e['DELIVERY_ZIP'])


def build_payment():
    for env_var in ['CC_NUMBER', 'EXPIRATION', 'CVV', 'BILLING_ZIP']:
        _check_defined(env_var, "Required Payment Env Var {} is not defined!")
    e = os.environ
    return pizzapi.PaymentObject(number=e['CC_NUMBER'],
                                 expiration=e['EXPIRATION'],
                                 cvv=e['CVV'],
                                 zip=e['BILLING_ZIP'])


def build_order():
    cust = build_customer()
    addy = build_address()
    store = addy.closest_store()
    return pizzapi.Order(store=store,
                         customer=cust,
                         address=addy)


def _parse_items():
    """Finds Bash var MY_ORDER_ITEMS, a comma separated list of item codes
    compatible with the pizzapi package. See the README for pizzapi for more
    details on how to search for items"""
    for env_var in ['MY_ORDER_ITEMS']:
        _check_defined(env_var, "Required Order Env Var {} is not defined!")
    return os.environ['MY_ORDER_ITEMS'].split(",")


def order_pie(order):
    card = build_payment()
    order.credit_card = card
    items = _parse_items()
    for item in items:
        order.add_item(item)
    order.pay_with(card)
    # order.place(card)


class PizzaDeliveryHandler(IPythonHandler):

    def get(self):
        order = build_order()
        order_pie(order)
        # with open("PIZZA_CODE_RUNNING.txt", 'w') as f:
        #    f.write("Get the door. It's Dominos.\n")