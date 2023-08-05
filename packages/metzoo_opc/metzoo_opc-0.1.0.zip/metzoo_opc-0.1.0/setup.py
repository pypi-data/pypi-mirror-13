from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='metzoo_opc',
      version='0.1.0',
      description='OPC SDK for Metzoo',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='metzoo monitoring metric',
      url='https://bitbucket.org/edrans/metzoo-sdk/opc',
      author='Edrans',
      author_email='info@edrans.com',
      license='MIT',
      packages=['metzoo_opc'],
      install_requires=['metzoo','pyyaml','pyro','pyodbc'],
      zip_safe=False)