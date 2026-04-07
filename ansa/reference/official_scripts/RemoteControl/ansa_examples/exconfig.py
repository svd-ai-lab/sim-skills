import platform
import os

_BCS_VERSION = '19.1.0'


def _find_bcs_location():
	if platform.system() == 'Windows':
		if os.path.exists(r'C:\Program Files (x86)\BETA_CAE_Systems\ansa_v' + _BCS_VERSION + r'\ansa64.bat'):
			bcs_root = r'C:\Program Files (x86)\BETA_CAE_Systems'
		
		elif os.path.exists(os.path.join(os.getenv("LOCALAPPDATA"), 'Apps',
			  'BETA_CAE_Systems', 'ansa_v'+_BCS_VERSION, 'ansa64.bat')):
			bcs_root = os.path.join(os.getenv("LOCALAPPDATA"), 'Apps',
			  'BETA_CAE_Systems')
		
		else:
			bcs_root = ''
	else:
		bcs_root = ''

	return bcs_root


def get_app_location(app):
	if app not in ('ansa', 'meta', 'epilysis'):
		raise Exception
	
	a2e = {'ansa': 'ansa64', 'meta': 'meta_post64', 'epilysis': 'epilysis'}
	a2f = {'ansa': 'ansa_v' + _BCS_VERSION, 'meta': 'meta_post_v' + _BCS_VERSION, 'epilysis': 'ansa_v' + _BCS_VERSION}

	bcs_root = _find_bcs_location()
	if bcs_root: bcs_root = os.path.join(bcs_root, a2f[app])
	if platform.system() == 'Windows':
		return os.path.join(bcs_root, a2e[app] + '.bat')
	else:
		return os.path.join(bcs_root, a2e[app] + '.sh')
