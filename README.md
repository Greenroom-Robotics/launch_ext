# launch_ext - Launch Extensions

## Actions

### ExecuteProcessExt

### IncludePackageLaunchFile

### LogRotate

### SetLaunchConfigurationIfNotNone

### WriteFile

## Conditions

### EnumEqual

## Substitutions

### FileContents

### Templated

### ROSLoggers and ROSLogLevel
Substitutions for setting the levels of ROS node loggers.

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

