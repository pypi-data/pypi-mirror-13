from distutils.core import setup

setup(
    name='csvwriter',
    version='0.2.2',
    packages=['csvwriter'],
    url='https://github.com/aplavin/csvwriter',
    license='MIT',
    author='Alexander Plavin',
    author_email='alexander@plav.in',
    description='Simple convenience wrapper on top of csv.DictWriter.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
