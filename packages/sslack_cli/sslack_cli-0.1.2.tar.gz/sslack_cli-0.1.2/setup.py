import setuptools


setuptools.setup(
    name='sslack_cli',
    description='Plugin that gives sslack applications cli feature.',
    version='0.1.2',
    license='MIT license',
    platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
    author='magniff',
    author_email='tinysnippest@gmail.com',
    entry_points={
        'sslack42': ['sslack_cli=source.implementation']
    },
    install_requires=['sslack'],
    packages=setuptools.find_packages(),
    zip_safe=False,
)
