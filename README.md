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

### Unary

### WriteTempFile

### YAMLToFile

