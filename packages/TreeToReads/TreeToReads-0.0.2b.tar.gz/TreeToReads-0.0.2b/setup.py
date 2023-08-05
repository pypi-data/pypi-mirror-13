from setuptools import setup


setup(
    name='TreeToReads',
    version='0.0.2b',
    py_modules =['treetoreads',],
    license='No copyright',
    description = 'ree to Reads - A python script to to read a tree, resolve polytomes, generate mutations and simulate reads.',
    author = 'Emily Jane McTavish  ',
    author_email = 'ejmctavish@gmail.com',
    url = 'https://github.com/snacktavish/TreeToReads', # use the URL to the github repo
    long_description=open('README.md').read(),
    install_requires=[
          'dendropy',
      ],
)
