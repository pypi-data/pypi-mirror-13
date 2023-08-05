from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(name='pyoutube',
      version='0.5',
      description='Upload videos to youtube using OAuth2.0 and the youtube API',
      long_description=long_description,
      classifiers=['Development Status :: 4 - Beta',
                    'License :: OSI Approved :: MIT License',
                    'Programming Language :: Python :: 3',
					'Topic :: Internet :: WWW/HTTP',
					'Topic :: Multimedia :: Video'],
      license='MIT',
      keywords='youtube upload uploader', 
	  url='https://github.com/lpbrown999/pyoutube',
      author='lpbrown999',
      author_email='lpbrown999@gmail.com',
      packages=['pyoutube'],
      install_requires = ['google-api-python-client'],
	  include_package_data=True,
      zip_safe=False)