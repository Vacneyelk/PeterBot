# Contribution workflow

## Step 1: For the PeterBot repo

[fork](images/Fork.png)

## Step 2: Configure your environment

How you setup your environment is up to you. It's recommended to use [Docker](https://www.docker.com/). PeterBot is dockerized to make deploying the bot easy. All of your environment and database setup is handled with docker, you simply need to write the code.

If you would like your IDE to have code completion and type hints, I recommend installing `Python 3.10` (3.8+ should be okay), creating a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/), and installing the requirements file to your environment.

### Setting up the environment to run the bot.

* Install [Docker](https://docs.docker.com/get-docker/) for your OS
* Install [Docker compose](https://docs.docker.com/compose/install/) for your OS
* Install pre-commit hooks to your python environment `pip install pre-commit`
  * If you don't use pre-commit, ensure you apply [black](https://github.com/psf/black), [isort](https://pycqa.github.io/isort/), and [flake8](https://flake8.pycqa.org/en/latest/)
* Build the bot image with `docker-compose build`
  * This will build the bot image
* Run the bot with postgres `docker-compose up`

Note: remember to rebuild the bot each time make code changes.

### Setup up a local python environment.

You can install all requirements with `pip install -r requirements.txt`. **Make sure pip is for your virtual environment if you set one up.** It's highly recommended to use a virtual environment otherwise it might pollute your system python.

## Step 3: Prepare a PR

Ensure your code has been formatted with `black`, imports sorted with `isort`, and linted with `flake8`. **I will reject pull requests if you aren't doing this.**
If you think we should ignore a flake8 warning, please detail why in the PR.

Currently I'm not familiar enough with the PR process to really write much.