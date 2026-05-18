ARG ROS_DISTRO=jazzy
FROM ros:${ROS_DISTRO}-ros-base

ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3-colcon-common-extensions \
      python3-rosdep \
      python3-pip \
      git \
      sudo \
      bash-completion \
      vim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ros_ws
RUN rosdep update

COPY package.xml setup.py pytest.ini /ros_ws/src/launch_ext/
COPY resource /ros_ws/src/launch_ext/resource
COPY launch_ext /ros_ws/src/launch_ext/launch_ext
COPY test /ros_ws/src/launch_ext/test

RUN . /opt/ros/${ROS_DISTRO}/setup.sh \
    && apt-get update \
    && rosdep install --from-paths src --ignore-src -y \
    && rm -rf /var/lib/apt/lists/*

RUN . /opt/ros/${ROS_DISTRO}/setup.sh \
    && colcon build --event-handlers console_direct+

RUN . /opt/ros/${ROS_DISTRO}/setup.sh \
    && . /ros_ws/install/setup.sh \
    && ros2 pkg prefix launch_ext \
    && python3 -c "import launch_ext; print('launch_ext imported from', launch_ext.__file__)"
