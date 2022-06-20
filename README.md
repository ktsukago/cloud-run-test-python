# cloud-run-test-python

# Eventarc Python Samples


## Setup

1. Install [`pip`][pip] and [`virtualenv`][virtualenv] if you do not already have them.

    - You may want to refer to the [`Python Development Environment Setup Guide`][setup] for Google Cloud Platform for instructions.   

1. Create a virtualenv. Samples are compatible with Python 2.7 and 3.4+.

    ```sh
    virtualenv env
    source env/bin/activate
    ```

1. Install the dependencies needed to run the samples.

    ```sh
    pip install -r requirements.txt
    ```

1. Start the application

    ```sh
    python main.py
    ```

1. Test the application 

    ```sh
    pytest
    ```