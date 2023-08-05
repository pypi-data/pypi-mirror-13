from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(name='pyoutube',
      version='0.2.4',
      description='Upload videos to youtube using OAuth2.0 and the youtube API',
      long_description=long_description,
      classifieres=['Development Status :: 3 - Alpha',
                    'Programming Language :: Python :: 3.4'],
      liscense='MIT',
      keywords='youtube upload uploader', 
      author='lpbrown999',
      author_email='lpbrown999@gmail.com',
      packages=['pyoutube'],
      install_requires = ['google-api-python-client'],
      zip_safe=False)