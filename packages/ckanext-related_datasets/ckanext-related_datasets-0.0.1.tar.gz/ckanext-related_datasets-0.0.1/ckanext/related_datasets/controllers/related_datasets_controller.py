'''
Controller for related datasets
'''
import logging

from ckan.lib.base import BaseController
from ckan.model import Session, Package
import ckan.lib.helpers as h
from pylons import config
from ckan.common import json, request, response
import ckan.lib.base as base
import ckan.logic as logic
import requests
import pylons.config as config

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action


class RelatedDatasetsController(BaseController):
	def list(self):
		q = request.params['q']
		source = request.params['source']
		internal_only =config.get('ckan.related_datasets.internal', False)
		if internal_only:
			r = requests.get('https://www.exversion.com/api/v1/search?q=%s&source=%s' % (q, source), headers={'ckan-referral':source})
		else:
			r = requests.get('https://www.exversion.com/api/v1/search?q=%s' % (q,), headers={'ckan-referral':source})
		rj = r.json()
		if rj['status'] == 200:
			datasets = rj['body'][0:3]
		else:
			datasets = []
		response.headers['Content-type'] = 'application/json'
		return json.dumps({'datasets': datasets})