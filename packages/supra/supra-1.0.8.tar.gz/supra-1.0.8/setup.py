from distutils.core import setup
import os

# version (shape.function.path)
# python setup.py sdist upload
setup(
	name='supra',
	version='1.0.8',
	py_modules=['supra.views', 'supra.admin', 'supra'],
	url='https://github.com/luismoralesp/supra',
	author="Luis Miguel Morales Pajaro",
	author_email="luismiguel.mopa@gmail.com",
	licence="Creative Common",
	description="It's an easy JSON services generator",
	platform="Linux",
	data_files=[
		(os.pardir, ['supra.py']),
	]
)