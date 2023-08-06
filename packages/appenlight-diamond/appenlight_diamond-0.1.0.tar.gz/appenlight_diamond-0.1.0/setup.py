from setuptools import setup, find_packages


setup(name='appenlight_diamond',
      version='0.1.0',
      description='Python-Diamond handler for App Enlight (http://appenlight.com)',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: DFSG approved',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      author='Marcin Lulek',
      author_email='info@webreactor.eu',
      license='BSD',
      zip_safe=True,
      packages=find_packages(),
      include_package_data=True,
      package_data={
          '': ['*.txt', '*.rst', '*.ini', ]
      },
      install_requires=[
      ],
      entry_points="""
      """,
      test_suite='appenlight_diamond.tests'
)
