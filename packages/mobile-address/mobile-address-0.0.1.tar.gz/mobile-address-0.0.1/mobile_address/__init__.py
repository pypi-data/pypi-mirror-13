from .api import MobileAddress

def get_address(phone):
    _ = MobileAddress(phone)
    return _.get_full()

def get_province(phone):
    _ = MobileAddress(phone)
    return _.get_province()

def get_carrier(phone):
    _ = MobileAddress(phone)
    return _.get_carrier()
