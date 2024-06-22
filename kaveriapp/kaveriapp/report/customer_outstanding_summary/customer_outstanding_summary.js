// Copyright (c) 2024, Shahzad Naser and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Outstanding Summary"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
				reqd: 1
		},
		{
			fieldname: "posting_date",
			label: __("Date"),
			fieldtype: "Date",
			default: frappe.datetime.nowdate(),
			reqd: 1
		},
		{
			fieldname: "territory",
			label: __("Territory"),
			fieldtype: "Link",
			options: "Territory"
		}
	]
};
