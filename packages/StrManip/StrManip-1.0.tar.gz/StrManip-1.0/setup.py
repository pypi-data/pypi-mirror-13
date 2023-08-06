from distutils.core import setup

__version__ = '1.0'


setup(name='StrManip',
      version=__version__,
      description='clipboard string manipulation in Python',
      long_description=open('README.rst').read(),
      author='Ryan Pessa',
      author_email='dkived@gmail.com',
      url='https://github.com/kived/strmanip',

      py_modules=['strmanip'],
      requires=['Kivy (>=1.9.1)'],

      download_url='https://github.com/kived/strmanip/tarball/' + __version__,
      keywords=['tool', 'clipboard', 'string'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Win32 (MS Windows)',
          'Environment :: X11 Applications',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Text Processing',
          'Topic :: Utilities',
      ],
      )
