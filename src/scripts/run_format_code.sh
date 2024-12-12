#!/bin/bash

poetry shell

poetry run ruff check --fix
