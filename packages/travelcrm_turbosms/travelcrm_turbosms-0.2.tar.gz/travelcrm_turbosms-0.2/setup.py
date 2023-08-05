import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'travelcrm',
    'suds>=0.4'
]

setup(name='travelcrm_turbosms',
    version='0.2',
    description='travelcrm_turbosms',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
      "Programming Language :: Python",
      "Framework :: Pyramid",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
    author='Vitalii Mazur',
    author_email='vitalii.mazur@gmail.com',
    url='',
    keywords='web pyramid pylons travelcrm sms',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="travelcrm_turbosms",
    entry_points="""\
    [paste.app_factory]
    main = travelcrm_turbosms:main
    """,
    message_extractors={
        'travelcrm_turbosms': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('static/**', 'ignore', None)
        ]
    },
)
