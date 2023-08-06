#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import os
import re

import sarge
import yaml
from jinja2 import Environment, PackageLoader

from . import PACKAGE_PATH

FILENAME_TEMPLATE = {
    "python": "{category}_{number:03d}.py"
}


def create_attempt(challenge, language, overwrite=False):
    category = challenge["category"]
    number = challenge["number"]

    file_name = FILENAME_TEMPLATE.get(language).format(category=category, number=number)
    file_path = os.path.join(category, file_name)

    if os.path.exists(file_path) and not overwrite:
        raise ValueError("A file for this challenge was already created.")

    if not os.path.isdir(category):
        os.makedirs(category)

    env = Environment(loader=PackageLoader('challenge_me', 'templates'))
    template = env.get_template(language + ".template")
    result = template.render(challenge=challenge, category=category, filename=file_name)

    with open(file_path, "w") as output_file:
        output_file.write(result)


def verify(challenge, filename):

    os.chmod(filename, 0o755)

    for test in challenge["tests"]:
        input_text = str(test["input"])
        output_text = str(test["output"])
        command = sarge.capture_both(filename + " " + input_text)
        if command.stdout.text.strip() != output_text.strip():
            return False, input_text, output_text, command

    return True, None, None, None


def get_challenge_with_test(category, number):
    challenge = get_challenge(category, number)
    while challenge is not None and "tests" not in challenge:
        number += 1
        challenge = get_challenge(category, number)
    return challenge


def current_attempt_in_category(category):
    default_number = 1

    files = glob.glob(category + '/*[0-9][0-9][0-9]*.*')
    if not files:
        return default_number

    filename = max(files)
    number = re.search('.*(\d{3}).*', filename)
    if not number:
        return default_number

    return int(number.group(1))


def current_attempt():
    file_path = os.path.join(PACKAGE_PATH, "challenges")
    for filename in glob.glob(file_path + '/*.yaml'):
        category = re.search('.*/(.+)\.yaml', filename)
        if not category:
            continue
        category = category.group(1)

        with open(filename, "r") as challenge_file:
            number = current_attempt_in_category(category)

            if number <= len(list(yaml.load_all(challenge_file))):
                return category, number

    return None, -1


def get_challenge(category, number):
    file_name = os.path.join(PACKAGE_PATH, "challenges", category + ".yaml")
    with open(file_name, "r") as challenge_file:
        challenges = list(yaml.load_all(challenge_file))

    if number - 1 < len(challenges):
        challenge = challenges[number - 1]
        challenge["category"] = category
        challenge["number"] = number
        return challenge
    else:
        return None


def get_attempts(category, number):
    return glob.glob(category + '/*{:03d}*.*'.format(number))
