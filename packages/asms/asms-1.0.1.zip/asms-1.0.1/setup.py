import sys
from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

if sys.version_info < (3, 4):
    required_packages = ['enum34']
else:
    required_packages = []    


setup(name='asms',
      version='1.0.1',
      description='Provides SMS interface, enabling scripts to send text messages (SMSes) via aText mobile application',
      long_description=readme(),
      url='http://baseit.pl/#product-asms',
      download_url="http://baseit.pl/#dload-asms",
      author='baseIT',
      author_email='baseit.app+asms@gmail.com',
      maintainer='baseIT',
      maintainer_email='baseit.app+asms@gmail.com',
      license='MIT',
      packages=['asms'],
      scripts=['bin/sms.py'],
      install_requires=required_packages,
      include_package_data=True,
      zip_safe=False,
      keywords = "sms texting text atext telco",
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications',
        'Topic :: Communications :: Internet Phone',
        'Topic :: Communications :: Telephony',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: Microsoft :: MS-DOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix'        
      ])