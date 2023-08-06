from floraconcierge.shortcuts import get_apiclient


def count_month():
    return get_apiclient().services.discount.count_month()


def email(email):
    return get_apiclient().services.discount.email(email)
