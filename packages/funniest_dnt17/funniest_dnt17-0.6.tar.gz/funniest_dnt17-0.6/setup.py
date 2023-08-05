from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='funniest_dnt17',
        version='0.6',
        description='The funniest joke in the world',
        long_description='Really, the funniest around.',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7',
            'Topic :: Text Processing :: Linguistic',
        ],
        keywords='funniest joke comedy flying circus tutorial',
        url='https://github.com/dnt17/funniest_dnt17',
        author='Devin Turner',
        author_email='devinturner17@gmail.com',
        license='MIT',
        packages=['funniest_dnt17'],
        install_requires=[
            'markdown',
        ],
        include_package_data=True,
        zip_save=False,
        scripts=['bin/funniest-joke'],
        entry_points = {
            'console_scripts': ['funniest-joke=funniest_dnt17.command_line:main'],
        },
        test_suite='nose.collector',
        tests_require=['nose'],
)
