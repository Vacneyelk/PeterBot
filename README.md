# PeterBot

PeterBot aims to the one stop shop for all UCI Discord needs.

All code should be formatted and linted with

* [black](https://github.com/psf/black)
* [isort](https://pycqa.github.io/isort/)
* [flake8](https://flake8.pycqa.org/en/latest/)

You can install [pre-commit](https://pre-commit.com/) which will do this for you when you try and commit.

## Build and run the bot

On linux we can make use of the makefile commands.

Note: make sure you have assigned yourself the `docker` group.

### Building

`docker-compose build`

### Running the bot

`docker-compose up`

## Contributing

To start contributing check out the [contributing doc](CONTRIBUTING.md)