# syndle
[![PyPI version](https://badge.fury.io/py/syndle.svg)](https://badge.fury.io/py/syndle)
[![Build Status](https://travis-ci.org/Jintin/syndle.svg?branch=master)](https://travis-ci.org/Jintin/syndle)

syndle is an Gradle tool to help you clone dependencies into local maven.

## Installation
Simple install by [pip](http://pip.readthedocs.org/en/stable/installing):

```bash
$ sudo pip install syndle
```

## Usage
The most commonly used command:


```bash
$ syndle parse -p <path>                        
                                        # parse gradle project and download dependencies
$ syndle clone -p <package> -s <server1> <server2> ...
                                        # download specific dependencies into local maven
```

See `syndle --help` or `syndle <command> --help` for more information.

## TroubleShooting
If you encounter SSL problem like following maybe your python is too old. Try to update Python 2.7.14+ or use Python 3.
```bash
<urlopen error [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:590)>
```

## Contributing
Bug reports and pull requests are welcome on GitHub at [https://github.com/Jintin/syndle](https://github.com/Jintin/syndle).

## License
The package is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
