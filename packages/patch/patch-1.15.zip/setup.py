from distutils.core import setup

setup(
    name='patch',
    version='1.15',
    author='anatoly techtonik <techtonik@gmail.com>',
    url='https://github.com/techtonik/python-patch/',

    description='Patch utility to apply unified diffs',
    license='MIT',

    py_modules=['patch'],

    classifiers=[
        'Classifier: Programming Language :: Python :: 2 :: Only',
    ],
)
