import json
import os
from dataclasses import dataclass, field

from nlp_annotator_api.utils.update_dataclass import update_dataclass


@dataclass
class NlpConfig:
    num_workers: int = 2


@dataclass
class AuthConfig:
    api_key: str = None


@dataclass
class Config:
    auth: AuthConfig = field(default_factory=AuthConfig)
    nlp: NlpConfig = field(default_factory=NlpConfig)
    statsd: dict = field(default_factory=lambda: {"prefix": "nlp_annotator_api."})

    def update(self, config: dict):
        update_dataclass(self, config)

        return self

    def add_file(self, file_path: str, required=True):
        if os.path.isfile(file_path):
            with open(file_path, "r") as config_reader:
                config: dict = json.load(config_reader)

            return self.update(config)

        if required:
            raise RuntimeError(
                "Required file: %r is missing or isn't a file" % file_path
            )

    def add_json_env_var(self, var_name: str, required=False):
        raw_config = os.getenv(var_name)

        if raw_config:
            config: dict = json.loads(raw_config)

            return self.update(config)

        if required:
            raise RuntimeError(
                "Missing or empty required environment variable %r" % var_name
            )


def _create_config():
    result = Config()

    config_file_sources = os.getenv("NLP_API_CONFIG_FILES", "config.json").split(",")

    for f in config_file_sources:
        result.add_file(f.strip(), required=True)

    return result


conf = _create_config()
