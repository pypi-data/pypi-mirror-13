from distutils.core import setup

setup(
    name='schema-migrations',
    version='0.1.2',
    packages=['schema_migrations'],
    url='',
    license='MIT License',
    author='Darwin Monroy',
    author_email='contact@darwinmonroy.com',
    description='PostgreSQL Schema Migrations',
    install_requires=[
        'psycopg2'
    ]
)
