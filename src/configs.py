import json
import sys
from typing import Any

from jsf import JSF
from jsonschema import ValidationError, validate


def loadConfig(config_file: str, schema_file: str) -> list[dict]:
    with open(schema_file, "r") as f:
        schema = json.load(f)
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        validate(config, schema)
        return config
    except FileNotFoundError:
        faker = JSF(schema)
        with open(config_file, "w+") as file:
            json.dump(faker.generate(use_defaults=True), file, indent=4)
        print(
            f"'{config_file}' is missing! A clean '{config_file}' has been generated for you."
        )
        return []
    except ValidationError as e:
        print(f"[{config_file}]", e)
        sys.exit(1)
