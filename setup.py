import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'alembic',
    'plaster_pastedeploy',
    'pyramid >= 1.9',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_retry',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'pyramid_openapi3',
    'psycopg2-binary',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest>=3.7.4',
    'pytest-cov',
]

setup(
    name='setara_backend',
    version='1.0',
    description='B2B_Setara_Backend',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = setara_backend:main',
        ],
        'console_scripts': [
            'run_linter=setara_backend.scripts.run_linter:main',
            'migrate=setara_backend.scripts.alembic:main',
        ],
    },
)
