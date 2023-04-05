from setuptools import find_packages
from setuptools import setup

package_name = 'launch_ext'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=[
        'setuptools',
        'launch'
    ],
    zip_safe=True,
    author='Russ Webber',
    author_email='russ.webber@greenroomrobotics.com',
    # maintainer='Aditya Pande, Brandon Ong',
    # maintainer_email='aditya.pande@openrobotics.org, brandon@openrobotics.org',
    url='https://github.com/Greenroom-Robotics/launch_ext',
    download_url='https://github.com/Greenroom-Robotics/launch_ext/releases',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Some extras for `launch` tooling.',
    long_description=(
        'Some extras for `launch` tooling.'
    ),
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'launch.frontend.launch_extension': [
            'launch_ext = launch_ext',
        ],
    }
)
