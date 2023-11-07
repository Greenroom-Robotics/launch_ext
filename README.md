# launch_ext - Launch Extensions

## Actions

### ExecuteProcessExt

### IncludePackageLaunchFile

### LogRotate

### MakeDeviceNode

This is used to create Linux device nodes for USB devices that are not automatically created by the kernel or when udev is not permitted.

```python
MakeDeviceNode("/dev/tty-magnetometer", "ttyUSB", "Prolific Technology Inc.", "USB-Serial Controller D")
```

Will create a device node at `/dev/tty-magnetometer` if it does not already exist. The device node will be created if the USB device with the vendor name `Prolific Technology Inc.` (ID `067b`) and product name `USB-Serial Controller D` (ID `2303`) is connected.

### SetLaunchConfigurationIfNotNone

### WriteFile

## Conditions

### EnumEqual

## Substitutions

### Templated

### ROSLoggers and ROSLogLevel
Substitutions for setting the levels of ROS node loggers.

**NOTE: This unfortunately requires the `name` argument of each `Node` to be set at the moment.**

```python
ros_arguments=["--log-level", ROSLogLevel("debug")]
```

Will set only the node's log level to `debug`. (Equivalent to `--log-level node_name:=debug`)

```python
ros_arguments=["--log-level", ROSLogLevel("debug", all_loggers=True)]
```

Will set all loggers to `debug`. (Equivalent to `--log-level debug`)

```python
ros_arguments=[*ROSLoggers("debug", {'rcl': 'debug', 'rmw_fastrtps_cpp': 'info'})]
```

Will set the node's log level to `debug`, `rcl` to `debug` and `rmw_fastrtps_cpp` to `info`.
(Equivalent to `--log-level node_name:=debug --log-level rcl:=debug --log-level rmw_fastrtps_cpp:=info`)

### Unary

### WriteTempFile

### YAMLToFile

