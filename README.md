[![Build Status](https://travis-ci.org/drmobile/services-lib.svg?branch=master)](https://travis-ci.org/drmobile/services-lib)
# services-lib
Library for back-end services which include common functions/scripts/libraries.

# Document
http://soocii-services-lib.readthedocs.io/en/latest/

## Installation
```commandline
pip install soocii-services-lib
```

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
### Setup Environment
```commandline
pip install -e .[test]
```

### Run Test
You can use `pyenv` to install 3.3.6 and 3.5.3.

```commandline
tox
```

### Deploy to PYPI
1. Update version number in setup.py. Follow [Semantic Version](http://semver.org/) 
2. Send a PR on `develop` branch
3. Create a PR to merge `develop` branch into `master` branch
4. Tag `master` branch with version
