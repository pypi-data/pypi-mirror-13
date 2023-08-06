from setuptools import setup

entry_points = {
    'console_scripts': [
        'whatportis=whatportis.main:run',
    ]
}
requirements = open('requirements.txt').read()
readme = open('README.rst').read()

setup(
    name="whatportis",
    version="0.2",
    url='http://github.com/ncrocfer/whatportis',
    author='Nicolas Crocfer',
    author_email='ncrocfer@gmail.com',
    description="A command to search port names and numbers",
    long_description=readme,
    packages=['whatportis'],
    include_package_data=True,
    install_requires=requirements,
    entry_points=entry_points,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ),
)