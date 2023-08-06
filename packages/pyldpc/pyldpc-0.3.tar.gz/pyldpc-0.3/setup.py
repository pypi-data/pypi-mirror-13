from setuptools import setup 

def readme():
	with open('README.rst') as f:
		return f.read()
		
setup(name='pyldpc',
      version='0.3',
      description='Simulation of Low Density Parity Check Codes',
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
      keywords='codes ldpc image decoding coding callager',
      url='https://github.com/janatiH/pyldpc',
      author='Hicham Janati',
      author_email='hicham.janati@outlook.fr',
      license='MIT',
      packages=['pyldpc'],
      zip_safe=False)