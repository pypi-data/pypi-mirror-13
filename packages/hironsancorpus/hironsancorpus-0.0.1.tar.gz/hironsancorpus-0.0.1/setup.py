from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description=f.read()


setup(
    name='hironsancorpus',
    version='0.0.1',
    description='Japanese IOB2 tagged corpus for named entity recognition.',
    long_description=long_description,
    url='https://github.com/Hironsan/hironsan_corpus',
    download_url='',
    author='Hironsan',
    author_email='light.tree.1.13@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords=['corpus', 'IOB', 'named entity recognition', 'japanese corpus'],
    packages=find_packages(exclude=['tests*']),
)