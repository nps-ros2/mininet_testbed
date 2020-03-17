from setuptools import find_packages
from setuptools import setup

package_name = 'testbed_nodes'

setup(
    name=package_name,
    version='0.6.2',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Bruce Allen',
    author_email='bdallen@nps.edu',
    maintainer='Bruce Allen',
    maintainer_email='bdallen@nps.edu',
    keywords=['ROS'],
    classifiers=[
        'Programming Language :: Python'
    ],
    description=(
        'Mininet-WiFi testbed nodes.'
    ),
    license='your license',
    entry_points={
        'console_scripts': [
            'testbed_robot = testbed_nodes.testbed_robot:main'
        ],
    },
)
