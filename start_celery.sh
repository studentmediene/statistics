#!/bin/bash
celery -A statistics worker -B -l info
