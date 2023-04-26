import os
from glob import glob
from setuptools import setup

package_name = 'test_api'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='MangDang',
    author_email='fae@mangdang.net',
    maintainer='MangDang',
    maintainer_email='fae@mangdang.net',
    description='The test_api package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'test_display = test_api.test_display:main',
            'test_servos = test_api.test_servos:main'
        ],
    },
)
