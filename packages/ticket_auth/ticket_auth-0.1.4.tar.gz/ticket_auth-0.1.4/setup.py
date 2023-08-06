from setuptools import setup

setup(
    name="ticket_auth",
    version='0.1.4',
    description='Ticket authentication system similar to mod_auth_tkt used by Apache',
    long_description=open('README.rst').read(),
    packages=['ticket_auth'],
    author='Gnarly Chicken',
    author_email='gnarlychicken@gmx.com',
    test_suite='tests',
    url='https://github.com/gnarlychicken/ticket_auth',
    license='MIT',
    classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Internet :: WWW/HTTP :: Session',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
    keywords='mod_auth_tkt authentication session ticket')
