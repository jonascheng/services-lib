[![Build Status](https://travis-ci.org/drmobile/services-lib.svg?branch=master)](https://travis-ci.org/drmobile/services-lib)
# services-lib
Library for back-end services which include common functions/scripts/libraries.

## Installation
`pip install -e git+https://github.com/drmobile/services-lib#egg=serviceslib`

or add following line in requirement.txt

`-e git+https://github.com/drmobile/services-lib#egg=serviceslib`

## click.py
### Basic Usage
```python
import click
from soocii_services_lib.click import CiTools, build_soocii_cli

tools = CiTools('vision')
soocii_cli = build_soocii_cli(tools)
click.CommandCollection(sources=[soocii_cli])
```

### Customized Specific Command
```python
import os
import click
from soocii_services_lib.click import CiTools, build_soocii_cli


def setup_env():
    os.environ['SECRET'] = "thisisasecret"

class MyCiTools(CiTools):
    def build(self):
        setup_env()
        super().build()
        
tools = MyCiTools('pepper')
soocii_cli = build_soocii_cli(tools)
cli = click.CommandCollection(sources=[soocii_cli])
```

## Development
### Run Test
You can use `pyenv` to install 3.3.6 and 3.5.3.

```commandline
tox
```
