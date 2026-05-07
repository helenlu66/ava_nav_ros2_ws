from setuptools import setup


package_name = 'nav2_demo'


setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/loading_pose.yaml', 'config/unloading_pose.yaml']),
        ('share/' + package_name + '/launch', ['launch/delivery_node.launch.py']),
    ],
    install_requires=['setuptools', 'PyYAML'],
    zip_safe=True,
    maintainer='hrilab',
    maintainer_email='hrilab@todo.todo',
    description='Small Nav2 demo utilities for named poses.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'delivery_node = nav2_demo.delivery_node:main',
        ],
    },
)