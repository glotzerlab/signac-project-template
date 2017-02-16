#!/bin/bash

python -m my_project.status --detailed --parameters p $@ | tee status.txt
