# rOSi
Extensible robot control application

## Settings
A file named `settings.py` in the application root will be readed for application configuration and module loading.

Here's an example of how this file looks like:

```python
# load module names
import profiles

# Name of the robot's profile directory (this directory is located in the folder: profiles)
PROFILE = 'simubot'

# Modules to load
MODULES = profiles.WebHUD | profiles.ordex

# Log
LOG = False
```
