# Copyright (c) 2023, Ajna Cloud and contributors
# For license information, please see license.txt

import frappe
import math

from frappe.model.document import Document
from frappe.utils import random_string

class PharmaContainerCode(Document):
    def before_save(self):
        if self.is_new():
            self.sscc = str(self.name)
            check = checkdigit(self.name)
            self.check_digit = check
            self.name = f"{self.name}{check}"
            self.barcode = f"{self.name}"


@frappe.whitelist()
def calculate_sscc_check_digit(sscc: str) -> str:
    digits = [int(c) for c in sscc]
    check_digit = (10 - sum(digits[i] * 3**i % 10 for i in range(len(sscc)-1))) % 10
    return str(check_digit)

@frappe.whitelist()
def checkdigit(input):
    array = list(input)
   # print(array)
    total = 0

    ind = 1
    for i in array:
        if ind % 2 == 0:
            total += int(i)
        else:
            total += int(i)*3
        ind += 1
    divid = total//10
    divMod = total%10
    if divMod == 0:
        return 0
    plus_1 = divid+1
    into_10 = plus_1*10
    return int(into_10 - total)
