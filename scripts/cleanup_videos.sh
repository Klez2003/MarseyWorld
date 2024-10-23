#!/bin/bash

find /videos -not -name "*.mp4" -type f -delete
find /videos -name "*-t.mp4" -type f -delete