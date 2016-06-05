# rosie
Extensible robot control application

## Getting started
Before you start you must install the dependencies:

```sh
$ pip install -r requirements.txt
```

When everything its correctly [configured](#settings) you can run **rosie** like this:

```sh
$ ./rosie.py start
```

## Settings
A file named `config` in the application root will be readed for application configuration and module loading.

Here's an example of how this file looks like:

```cfg
[general]
profile = simubot

[ordex]
active = True

[restAPI]
active = True
```
