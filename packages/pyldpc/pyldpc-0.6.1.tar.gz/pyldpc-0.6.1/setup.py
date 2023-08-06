try:
	from setuptools import setup
except ImportError:
    from distutils.core import setup

	
def readme():
	with open('README.rst') as f:
		return f.read()
		
if __name__ == "__main__":
		
	setup(name='pyldpc',
		version='0.6.1',
		description='Simulation of Low Density Parity Check Codes & Applications',
		long_description=readme(),
		classifiers=[
			'Programming Language :: Python :: 3.4',
			'Development Status :: 4 - Beta',
			'Environment :: MacOS X',
			'Framework :: IPython',
			'Intended Audience :: Developers',
			'Intended Audience :: Education',
			'Intended Audience :: Science/Research',
			'Intended Audience :: Telecommunications Industry',
			'Natural Language :: English',
			'Natural Language :: French'
		],
		keywords='codes ldpc image decoding coding sound transmission',
		url='https://github.com/janatiH/pyldpc',
		author='Hicham Janati',
		author_email='hicham.janati@outlook.fr',
		license='MIT',
		packages = ['pyldpc'],
		install_requires = ['numpy'],
		zip_safe=False)