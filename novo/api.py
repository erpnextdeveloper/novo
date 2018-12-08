from __future__ import unicode_literals
import frappe
from frappe.utils import cint, get_gravatar, format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,get_last_day
from frappe import throw, msgprint, _
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils.password import update_password as _update_password
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe.desk.notifications import clear_notifications
from frappe.utils.user import get_system_managers
import frappe.permissions
import frappe.share
import re
import string
import random
import json
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import collections
import math
import logging
from frappe.client import delete
import traceback
import urllib
import urllib2
from erpnext.accounts.utils import get_fiscal_year
from collections import defaultdict



@frappe.whitelist()
def app_error_log(title,error):
	d = frappe.get_doc({
			"doctype": "App Error Log",
			"title":str("User:")+str(title),
			"error":traceback.format_exc()
		})
	d = d.insert(ignore_permissions=True)
	return d	

@frappe.whitelist()
def generateResponse(_type,status=None,message=None,data=None,error=None):
	response= {}
	if _type=="S":
		if status:
			response["status"]=status
		else:
			response["status"]="200"
		response["message"]=message
		response["data"]=data
	else:
		error_log=appErrorLog(frappe.session.user,str(error))
		if status:
			response["status"]=status
		else:
			response["status"]="500"
		if message:
			response["message"]=message
		else:
			response["message"]="Something Went Wrong"		
		response["message"]=message
		response["data"]=None
	return response


@frappe.whitelist()
def makeBOM(self,method):
	try:
		for row in self.items:
			#frappe.msgprint("Test")
			if not row.bom_no:
				template=frappe.db.sql("""select material_serial from `tabItem` where name=%s""",row.item_code)
				if template:
					garment_details=frappe.get_doc("Garment Type",template[0][0])
					if garment_details.bom_feeder:
						bom_temp_doc=frappe.get_doc("BOM Feeder",garment_details.bom_feeder)

						bom_material=[]
						for row1 in bom_temp_doc.items:
							bom_json={}
							if row1.item_type=="Fabric":
								bom_json["item_code"]=row.fabric_no
								bom_json["qty"]=row1.qty

							elif row1.item_type=="Lining":
								if row.lining_no:
									bom_json["item_code"]=row.lining_no
									bom_json["qty"]=row1.qty
								else:
									bom_json["item_code"]=row1.item
									bom_json["qty"]=row1.qty
								

							elif row1.item_type=="Buttons":
								if row.button:
									bom_json["item_code"]=row.button
									bom_json["qty"]=row1.qty
								else:
									bom_json["item_code"]=row1.item
									bom_json["qty"]=row1.qty
								
							else:
								bom_json["item_code"]=row1.item
								bom_json["qty"]=row1.qty

							bom_material.append(bom_json)

						bom_no=makeFGBOM(row.item_code,bom_temp_doc.company,bom_temp_doc.currency,bom_material,self.name)
						if bom_no:
							frappe.db.sql("""update `tabSales Order Item` set bom_no=%s where name=%s""",(bom_no,row.name))	
							msg='BOM Created:'+'<a href="#Form/BOM/'+bom_no+'">'+bom_no+'</a>'
							frappe.msgprint(msg)
					else:
						frappe.throw("BOM Feeder Not Available For Garment {0} And Item {1}".format(template[0][0],row.item_code))


	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


def makeFGBOM(item_code,company,currency,item_details,sales_order):
	try:
		doc=frappe.get_doc({
				"docstatus": 0,
				"doctype": "BOM",
				"owner":frappe.session.user,
				"quantity": 1,
				"rm_cost_as_per": "Valuation Rate",
				"company":str(company),
				"items":item_details,
				"item":str(item_code),
				"currency":str(currency),
				"sales_order":str(sales_order)
				})
		doc1=doc.insert()
		if doc1:
			return doc1.name

	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))

@frappe.whitelist()
def makeMultiplePO(doc_name):
	sales_order_details=frappe.get_doc("Sales Order",doc_name)
	msg=''
	for row in sales_order_details.items:
		po_no=makeProductionOrder(row.item_code,row.bom_no,row.qty,doc_name,row.name,row.warehouse,row.drawing_no,sales_order_details.measurement)
		if po_no:
			msg=msg+'<a href="#Form/Production Order/'+po_no+'">'+po_no+'</a>'+','
	return msg


@frappe.whitelist()
def makeMultipleSamplePO(doc_name):
	sales_order_details=frappe.get_doc("Sales Order",doc_name)
	msg=''
	for row in sales_order_details.items:
		po_no=makeSampleProductionOrder(row.item_code,row.qty,doc_name,row.name,row.drawing_no,sales_order_details.measurement)
		if po_no:
			msg=msg+'<a href="#Form/Production Order/'+po_no+'">'+po_no+'</a>'+','
	return msg
	




@frappe.whitelist()
def makeProductionOrder(item_code,bom,qty,sales_order,sales_order_item,warehouse,d_no=None,measurement_no=None):
	try:
		bom_details=frappe.get_doc("BOM",bom)
		bom_details.submit()
		parameter=frappe.get_doc("Parameter Table","Parameter")
		production_order = frappe.get_doc(dict(
				doctype='Production Order',
				production_item=item_code,
				bom_no=bom,
				qty=qty,
				company=bom_details.company,
				sales_order=sales_order,
				sales_order_no=sales_order,
				sales_order_item=sales_order_item,
				fg_warehouse=parameter.production_order_warehouse,
				drawing_no=d_no if not d_no==None else '',
				measurement_no=measurement_no if not measurement_no==None else ''
		)).insert()
		production_order.set_production_order_operations()
		production_order.submit()
		
		if production_order.name:
			#addPODetailsINSalesOrder(production_order.name,sales_order,'Main')
			return production_order.name

	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))

@frappe.whitelist()
def makeSampleProductionOrder(item_code,qty,sales_order,sales_order_item,d_no=None,measurement_no=None):
	try:
		#po_no=frappe.db.sql("""select name from `tabProduction Order` where sales_order=%s""",(sales_order)
		#if not po_no:
		#	frappe.throw("Can't Create Sample Production Order Before Main Production Order")
		#else:
		garment_type=frappe.db.sql("""select material_serial from `tabItem` where name=%s""",item_code)
		if garment_type:
			garment_details=frappe.get_doc("Garment Type",garment_type[0][0])
			if not garment_details.sample_item:
				frappe.throw("Select Sample Item For Garment {0}".format(garment_type[0][0]))
			elif not garment_details.sample_bom:
				frappe.throw("Select BOM For Sample Item In Garment {0}".format(garment_type[0][0]))
			else:
			
			
				bom_details=frappe.get_doc("BOM",garment_details.sample_bom)
				parameter=frappe.get_doc("Parameter Table","Parameter")
				production_order = frappe.get_doc(dict(
						doctype='Production Order',
						production_item=garment_details.sample_item,
						bom_no=bom_details.name,
						qty=1,
						company=bom_details.company,
						sales_order_no=sales_order,
						sample_production_order=1,
						sales_order_item=sales_order_item,
						fg_warehouse=parameter.production_order_warehouse,
						drawing_no=d_no if not d_no==None else '',
						measurement_no=measurement_no if not measurement_no==None else ''
				)).insert()
				production_order.set_production_order_operations()
				production_order.submit()
				if production_order.name:
						#addPODetailsINSalesOrder(production_order.name,sales_order,'Sample')
						return production_order.name

	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


def makePOName(self,method):
	try:
		if not self.sample_production_order:
			so_no=self.sales_order_no
			no=so_no[4:]
			item_doc=frappe.get_doc("Sales Order Item",self.sales_order_item)
			self.name='PROD '+str(no)+'/'+str(item_doc.idx)
		else:
			names = frappe.db.sql_list("""select name from `tabProduction Order` where sales_order_no=%s""", self.sales_order_no)
			if names:
				# name can be BOM/ITEM/001, BOM/ITEM/001-1, BOM-ITEM-001, BOM-ITEM-001-1

				# split by item
				#names = [name.split(self.item)[-1][1:] for name in names]

				# split by (-) if cancelled
				names = [cint(name.split('-')[-1]) for name in names]

				idx = max(names) + 1
			else:
				idx = 1

			so_no=self.sales_order_no
			no=so_no[4:]
			item_doc=frappe.get_doc("Sales Order Item",self.sales_order_item)
			self.name='SAMP '+str(no)+'/'+str(item_doc.idx)+ ('-%.1i' % idx)

			#self.name = self.production_order.replace('PROD','SAMP') + ('-%.1i' % idx)
		


	except Exception as e:
		error_log=app_error_log(frappe.session.user,str(e))


def id_generator(size):
   return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))


def addPODetailsINSalesOrder(po_name,so_name,po_type):
	data=frappe.db.sql("""insert into `tabProduction Order Details` (name,parenttype,parent,po_type,production_order) values('Sales Order','"""+so_name+"""','"""+po_type+"""','"""+po_name+"""')""")


@frappe.whitelist()
def makebomname():
	names = frappe.db.sql_list("""select name from `tabBOM`""")

	if names:
		# name can be BOM/ITEM/001, BOM/ITEM/001-1, BOM-ITEM-001, BOM-ITEM-001-1
			# split by item
		#names = [name.split(self.item)[-1][1:] for name in names]
			# split by (-) if cancelled
		names = [cint(name.split(' ')[-1]) for name in names]
		idx = max(names) + 1
	else:
		idx = 1

	self.name = 'BOM '+('-%.6i' % idx)



@frappe.whitelist()
def addTaxInItem():
	items=frappe.db.sql("""select name from `tabItem` where item_group='Main Fabric'""")
	item_tax='[{"tax_type":"IGST - BCC","tax_rate":5},{"tax_type":"CGST - BCC","tax_rate":2.5},{"tax_type":"SGST - BCC","tax_rate":2.5}]'
	if items:
		for row in items:
			doc=frappe.get_doc("Item",row[0])
			doc.taxes=dict(item_tax)
			doc.save()
	




	



	

