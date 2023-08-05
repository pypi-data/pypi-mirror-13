from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-ajax-favorite',
    version='1.0.0.dev1',
    author=u'DREIDEV',
    author_email='info@dreidev.com',
    url='https://github.com/dreidev/django-favorites',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

         'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    description='Associates favorite functionality with any given model.',
    long_description='In addition like, vote, thumbs up  and follow functionalities are also supported',
    keywords='favorite unfavorite vote unvote like unlike thumbs up thumbs down follow unfollow development',
    zip_safe=False,
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
)