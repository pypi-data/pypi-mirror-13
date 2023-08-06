from setuptools import setup

setup(name='bitiverse',
      version='0.1.3',
      description='A Decentralized Web Page',
      url='www.bitiverse.com',
      author='Andrew Barisser',
      license='MIT',
      packages=['bitiverse'],
      install_requires=[
        'bitcoin',
        'pycoin',
        'Pillow',
        'requests',
        'pybitcointools',
        'ecdsa'
      ],
      zip_safe=False)
