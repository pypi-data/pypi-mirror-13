from setuptools import setup, find_packages

setup(
    name='django-feedme',
    version='2.0.1',
    zip_safe=False,
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    url='http://github.com/dstegelman/django-feedme',
    license='MIT',
    author='Derek Stegelman',
    author_email='email@stegelman.com',
    description='Django Google Reader Replacement',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
    ],
    install_requires=[
        'feedparser==5.1.3,<6.0',
        'django-bootstrap-static>=2.0,<3.0',
        'lxml',
        'django-infuse>=0.3'
    ]
)
