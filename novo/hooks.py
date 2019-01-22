# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "novo"
app_title = "Novo"
app_publisher = "Novo"
app_description = "Novo"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "maheshwaribhavesh95863@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/novo/css/novo.css"
# app_include_js = "/assets/novo/js/novo.js"

# include js, css files in header of web template
# web_include_css = "/assets/novo/css/novo.css"
# web_include_js = "/assets/novo/js/novo.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "novo.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "novo.install.before_install"
# after_install = "novo.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "novo.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Order": {
		"on_submit": "novo.api.makeBOM"
	},
	"Production Order": {
		"autoname": "novo.api.makePOName"
	},
	"BOM": {
		"after_autoname": "novo.api.makebomname"
	},
	"Measurement":{
		"after_insert":"novo.api.makeVisitFromMeasurement"
	},
	"Appointment": {
		"after_insert": "erpnext.sms_api.sendAppointmentConfirmation"
	}


}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"daily": [
		"erpnext.api.changeCurrencyExchange"
	],
    	"cron": {
		"17 00 * * *": [
			"erpnext.sms_api.msgReminder"
	]
	}
}



# scheduler_events = {
# 	"all": [
# 		"novo.tasks.all"
# 	],
# 	"daily": [
# 		"novo.tasks.daily"
# 	],
# 	"hourly": [
# 		"novo.tasks.hourly"
# 	],
# 	"weekly": [
# 		"novo.tasks.weekly"
# 	]
# 	"monthly": [
# 		"novo.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "novo.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "novo.event.get_events"
# }

