import os


class Config(object):
	# py -c 'import os; print(os.urandom(16))'

	SECRET_KEY = os.environ.get('SECRET_KEY') or "b'\xd8\x8eC+\x9d\xc1{\x01\xd0\xeb\xa8m\x16\x13\x99\xaf'"

	MONGODB_SETTINGS = { 'db': 'UTA_Enrollment' }