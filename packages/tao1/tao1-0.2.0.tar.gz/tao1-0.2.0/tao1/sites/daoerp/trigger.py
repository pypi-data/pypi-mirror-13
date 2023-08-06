from core.core import *

def make_events():
	return  {
		'des:ware_attr/on_update_row': update_curr,
		'des:ware_attr/on_create_row':None,
		'des:ware_attr/on_del_row':None,
		'des:ware_attr/on_update_subtable':None,
		'des:ware_attr/on_create_subtable':None,

	}

def update_curr(doc_id):
	pass
