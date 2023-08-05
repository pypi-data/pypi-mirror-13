from setuptools import setup


setup(name='Alfe',
      version='0.1.0',
      py_modules=['index'],
      description='Extract TODO comment tags from source files',
      author='Ada Vasiliu',
      url='https://github.com/cyluun/alfe',
      license='MIT',
      install_requires=[
          'Click'
          ],
      entry_points='''
        [console_scripts]
        alfe=index:cli
      ''',
      )
