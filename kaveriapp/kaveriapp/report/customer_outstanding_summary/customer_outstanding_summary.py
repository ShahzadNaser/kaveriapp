# Copyright (c) 2024, Shahzad Naser and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import date_diff, getdate

def execute(filters=None):
	if not filters:
		filters = {}

	columns = [
		_("Customer ID") + ":Link/Customer:150",
		_("Customer Name") + ":Data:200",
		_("Company") + ":Link/Company:150",
		_("Territory") + ":Link/Territory:130",
		_("Sales Rep") + ":Data:150",
		_("Mobile") + ":Data:120",
		_("Credit Limit") + ":Currency:120",
  		_("Outstanding") + ":Currency:120",
  		_("Invoice Amount") + ":Currency:120",
  		_("Invoice Day") + ":Data:80",
		_("Payment Amount") + ":Currency:120",
  		_("Payment Day") + ":Data:80",
	]

	customers_data = get_data(filters)
	invoice_data = get_invoice_data(filters)
	payment_data = get_payment_data(filters)
	t_invoice_data = {}
	t_payment_data = {}
	for row in invoice_data:
		if row.get("customer") not in t_invoice_data:
			t_invoice_data[row.get("customer")] = row

	for row in payment_data:
		if row.get("customer") not in t_payment_data:
			t_payment_data[row.get("customer")] = row


	t_data = []
	for row in customers_data:
		if row.get("customer") in t_invoice_data:
			row.invoice_amount = t_invoice_data[row.get("customer")].get("amount")
			row.invoice_days = date_diff(getdate(filters.get("posting_date")), getdate(t_invoice_data[row.get("customer")].get("posting_date")))+1
   
		if row.get("customer") in t_payment_data:
			row.payment_amount = t_payment_data[row.get("customer")].get("amount")
			row.payment_days = date_diff(getdate(filters.get("posting_date")), getdate(t_payment_data[row.get("customer")].get("posting_date")))+1
		if not filters.get("territory") or  row.get("territory") == filters.get("territory"):
			t_data.append([
				row.customer,
				row.customer_name,
				filters.get("company"),
				row.territory,
				row.sales_rep,
				row.mobile_no,
				row.credit_limit,
				row.outstanding,
				row.invoice_amount,
				row.invoice_days,
				row.payment_amount,
				row.payment_days
			])
	return columns, t_data


def get_data(filters={}):

	return frappe.db.sql("""
		SELECT
			cust.name as customer,
			cust.customer_name as customer_name,
			cust.territory,
			(select territory_manager from `tabTerritory` where cust.territory=name ) as sales_rep,
			cust.mobile_no,
			(SELECT sum(credit_limit) from `tabCustomer Credit Limit` where parent = cust.name) as credit_limit,
			COALESCE(sum(gle.debit_in_account_currency) - sum(gle.credit_in_account_currency),0) as outstanding,
			' ' as invoice_amount,
			' ' as invoice_days,
			' ' as payment_amount,
			' ' as payment_days
		FROM
			`tabCustomer` cust
		LEFT JOIN
			`tabGL Entry` gle
			ON
				gle.party = cust.name and gle.party_type = 'Customer'

		WHERE
			cust.disabled=0 and gle.posting_date <= '{}' and gle.company = '{}'
		GROUP BY
			cust.name     
		""".format(filters.get("posting_date"),filters.get("company")),as_dict=True)

def get_invoice_data(filters={}):

	return frappe.db.sql("""
		SELECT
			si.customer,
			si.posting_date,
			si.grand_total as amount
		FROM
			`tabSales Invoice` si
		INNER JOIN
			(SELECT 
				MAX(name) as invoice_id
			FROM
				`tabSales Invoice`
			WHERE
				is_return=0 and docstatus = 1 and posting_date <= '{}' and company = '{}'
			GROUP BY
				customer) tsi
			ON tsi.invoice_id = si.name
		WHERE
			si.docstatus = 1 and si.posting_date <= '{}' and si.company = '{}'
		GROUP BY
			si.customer    
		""".format(filters.get("posting_date"),filters.get("company"),filters.get("posting_date"),filters.get("company")),as_dict=True)


def get_payment_data(filters={}):

	return frappe.db.sql("""
		SELECT
			pi.party as customer,
			pi.posting_date,
			pi.paid_amount as amount
		FROM
			`tabPayment Entry` pi
		INNER JOIN
			(SELECT 
				MAX(name) as pid
			FROM
				`tabPayment Entry`
			WHERE
				posting_date <= '{}' and company = '{}'
			GROUP BY
				party) tpi
			ON tpi.pid = pi.name
		WHERE
			pi.docstatus = 1 and pi.posting_date <= '{}' and pi.company = '{}'
		GROUP BY
			pi.party
		""".format(filters.get("posting_date"),filters.get("company"),filters.get("posting_date"),filters.get("company")),as_dict=True,debug=True)



