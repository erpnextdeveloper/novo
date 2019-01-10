# -*- coding: utf-8 -*-
# Copyright (c) 2018, Novo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt

class Drawing(Document):
	def autoname(self):
		if self.prefix:
			names = frappe.db.sql_list("""select name from `tabDrawing` where prefix=%s""", self.prefix)

			if names:
				names = [cint(name.split(' ')[-1]) for name in names]
				idx = max(names) + 1
			else:
				idx = 1

			self.name = self.prefix + (' %.6i' % idx)
		else:
			frappe.throw("Prefix Is Mandatory")
