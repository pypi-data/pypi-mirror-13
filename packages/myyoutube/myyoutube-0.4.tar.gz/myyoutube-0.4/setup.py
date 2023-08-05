from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(name='myyoutube',
      version='0.4',
      description='Upload videos to youtube using OAuth2.0 and the youtube API',
      long_description=long_description,
      classifieres=['Development Status :: 3 - Alpha',
                    'License :: OSI Approved :: MIT License',
                    'Programming Language :: Python :: 3.4'],
      license='MIT',
      keywords='youtube upload uploader', 
	  url='https://github.com/fingul/myyoutube',
      author='lpbrown999',
      author_email='fingul@gmail.com',
      packages=['myyoutube'],
      install_requires = ['google-api-python-client'],
	  include_package_data=True,
      zip_safe=False)