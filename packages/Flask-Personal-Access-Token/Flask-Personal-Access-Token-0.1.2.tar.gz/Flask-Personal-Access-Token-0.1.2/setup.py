"""
Flask Personal Access Token Managerment Extension.
"""

from setuptools import setup


setup(
    name='Flask-Personal-Access-Token',
    version='0.1.2',
    url='https://github.com/soasme/flask-personal-access-token',
    license='MIT',
    author='Ju Lin',
    author_email='soasme@gmail.com',
    description='Flask Personal Access Token Management Extension',
    long_description=__doc__,
    packages=['flask_personal_access_token'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
    ],
    classifiers=[
        'Framework :: Flask',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
