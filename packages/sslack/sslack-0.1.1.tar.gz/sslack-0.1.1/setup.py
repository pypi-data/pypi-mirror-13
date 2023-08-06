import setuptools


setuptools.setup(
    name='sslack',
    description='Plugable platform for slack bots deevlopment.',
    version='0.1.1',
    license='MIT license',
    platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
    author='magniff',
    author_email='tinysnippest@gmail.com',
    entry_points={
        'console_scripts': ['sslack=sslack:main_routine']
    },
    install_requires=['pytest', 'pluggy'],
    py_modules=['sslack'],
    packages=setuptools.find_packages(),
    zip_safe=False,
)
