#!/bin/bash

fclones group --cache /videos | fclones link
fclones group --cache /images | fclones link
fclones group --cache /audio | fclones link
fclones group --cache /songs | fclones link
fclones group --cache /asset_submissions | fclones link