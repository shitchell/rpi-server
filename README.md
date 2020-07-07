# rpi-server
Modular server allowing you to execute commands on a raspberry pi using HTTP requests

## Getting started

1. Download Python 3.x
2. Clone this repository
3. From within the repository, run `python3 serve.py`

## Modules

Extra commands can be added through modules. Each module is a python file that follows the naming pattern "rpi_*module-name*.py".

Within each module, commands are functions that follow the naming pattern "do_*command*()".

Commands are executed by visiting the url *http://[rpi-ip]:9000/module-name/command*

Several modules are provided as examples, although most require depenedencies to run.

## Docs

Visiting *http://[rpi-ip]:9000/* will provide a web based interface with automatically generated documentation.

Documentation is generated via typical python docstrings, eg:

```python
do_help(req, *args, **kwargs):
  """Provides documentation on commands"""
  ...
```

Samples can be provided by adding a list attribute to command methods, eg:

```python
do_help.samples = ["/help/reload", "/help/foo.bar"]
```

## Extending

To add commands, simply create a new module file that follows the naming convention "rpi_*module-name*.py", and then within that module add commands that follow the naming convention "do_*command*()". Each command should take the following arguments: req, \*args, \*\*kwargs.

**req**
The HTTP request received by the server. An instance of `SimpleHTTPRequestHandler`

**kwargs**
Anything in the url query string following the format `key=value`

**args**
Everything else in the url query string, ie: keys without a value

#### Example

1. Create the module "rpi_speech.py"
2. Create the command "do_say()"
```python
def do_say(req, *args, **kwargs):
  """Makes the raspberry pi say something"""
  message = kwargs.get("message")
  if message:
    engine = pyttsx3.init()
    engine.say("I will speak this text")
    engine.runAndWait()
do_say.samples = ["/speech/say?message=hello%20world"]
```
3. Visit the url *http://[rpi-ip]:9000/speech/say?message=hello%20world*
