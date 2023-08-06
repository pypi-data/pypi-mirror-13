from distutils.core import setup

# version (shape.function.path)
# python setup.py sdist upload
setup(
	name='supra',
	version='1.0.7',
	py_modules=['supra.views', 'supra.admin'],
	url='https://github.com/luismoralesp/supra',
	author="Luis Miguel Morales Pajaro",
	author_email="luismiguel.mopa@gmail.com",
	licence="Creative Common",
	description="It's an easy JSON services generator",
	platform="Linux",
	data_files=[
		('templates', ['supra/form.html', 'supra/json.html', 'list.html']),
		('templatetags', ['filters.py'])
	]
)