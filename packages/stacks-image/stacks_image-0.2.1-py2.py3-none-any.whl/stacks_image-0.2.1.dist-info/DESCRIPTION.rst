# Stacks Image

A Stacks application for handling images and lists of images.

## Dependencies

* `stacks-page` >= 0.1.1
* `django-versatileimagefield` >= 1.0.2
* `django-textplusstuff` >= 0.4

## Release Notes

### 0.2.1

* Increasing image field length to 300 characters.

### 0.2

* Added new 'attribution' field to `StacksImage`.

### 0.1.1

* Including templates in PyPI release.

### 0.1

* Initial open source release

## Running Tests

All commands below are run from within the `stacks-image` outer folder of this repo.

First create a new virtual environment and install the test requirements:

    $ pip install -r test_requirements.txt

Before running tests, first ensure this app passes a `flake8` linter check:

    $ flake8 stacks_image

Run the test suite with this command:

    $ coverage run --source=stacks_image runtests.py

See test coverage with this command:

    $ coverage report -m


