=====================
KavaHQ.com API client
=====================

Installation
============

.. code-block:: bash

   pip install kavahq-api

Usage
=====

.. code-block:: python

	import kavahq
	import keyring
	import getpass

	SERVICE = 'kavahq-api'
	username = 'imposeren'
	password = keyring.get_password(SERVICE, username)
	if password is None:
	    password = getpass.getpass()
	    keyring.set_password(SERVICE, username, password)

	api = kavahq.KavaApi(username=username, password=password, company_name='42 Coffee Cups')

	# almost all attributes of Api return instances of ApiObject which do not query results until they are required:
	projects_api = api.projects  # no requests made
	first_project_api = projects_api.children[0]  # project list api called but project details are not
	first_project_estimate_api = first_project_api.estimate  # zero apis called
	first_project_api.estimate['avg_time_per_cp']  # estimates api called and result is returned

	# you can also get all results of api as a dict:
	dict(first_project_api)

	# you can also get specific project api by it's slug:
	kava_project_api = api.projects.get('kavyarnya')
	dict(kava_project_api)
	# {u'days_num_bugs_showing': X, ...}

	dict(kava_project_api.estimate)
	# {u'avg_time_per_cp': u'2.1'...}
	kava_project_api.properties['owner']
	# u'akhavr'

	# as you can see api calls can be "chained":
	api.projects.estimate  # ApiObject for /api/project/estimate
	api.projects.properties  # ApiObject for /api/project/properties

	# but some attributes of ApiObject "break chaining":
	api.projects.children[0].estimate.response  # returns dict with response from API
	api.projects.get  # method to get projects by slug, (see examples above)
	api.projects.keys()  # will return keys of response dict


	# alternate way to call specific api:
	dict(api.projects.estimate.get(project='kavyarnya', company='42 Coffee Cups'))
	# this is equivivalent to:
	api.company_name = '42 Coffee Cups')
	dict(api.projects.get('kavyarnya').estimate)


Running tests
=============

.. code-block:: bash

   python setup.py nosetests
