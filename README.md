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

### LogRepoInfo

This will get the specified repository information and log it.
```python
LogRepoInfo("/path/to/repo")
```

### VerifyRepoCommit
This will verify the specified repository is at the specified commit hash. You can also specify whether to throw an exception of failure.

```python
VerifyRepoCommit("/path/to/repo", "<commit-hash>", pass_on_failure=False)
```

### VerifyRepoClean
This will verify the specified repository is clean. You can also specify whether to throw an exception of failure.
```python
VerifyRepoClean("/path/to/repo", pass_on_failure=False)
```

## Conditions

### EnumEqual

## Substitutions

### Templated

### Unary

### WriteTempFile

### YAMLToFile

