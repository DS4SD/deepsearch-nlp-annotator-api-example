import pathlib
import json
import os
from pydantic import BaseModel, Field, BaseSettings
from typing import Any, Optional, Dict, Tuple
from pydantic.env_settings import SettingsSourceCallable



class NlpConfig(BaseModel):
    num_workers: int = 2


class AuthConfig(BaseModel):
    api_key: Optional[str] = "test 123"


class RedisCacheConfig(BaseModel):
    url: str
    ttl: int = 300
    prefix: str = "nlp_annotator_cache"


class WatsonHealthAnnotatorConfig(BaseModel):
    api_url: str = "https://us-south.wh-acd.cloud.ibm.com/wh-acd/api"
    api_key: str = ""
    flow_name: str = "test-deepsearch_v3.0_default_flow"
    timeout_seconds: int = 600
    max_attempts: int = 5
    concepts: Dict = {}



def _make_json_settings_source(path: pathlib.Path):
    def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
        encoding = settings.__config__.env_file_encoding
        return json.loads(path.read_text(encoding))

    return json_config_settings_source


class Config(BaseSettings):
    auth: AuthConfig = Field(default_factory=AuthConfig)
    nlp: NlpConfig = Field(default_factory=NlpConfig)
    statsd: dict = Field(default_factory=lambda: {"prefix": "nlp_annotator_api."})
    redis_cache: Optional[RedisCacheConfig] = None
    watson_health_annotator: WatsonHealthAnnotatorConfig = Field(default_factory=WatsonHealthAnnotatorConfig)

    class Config:
        env_file_encoding = 'utf-8'

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:

            bases = init_settings, env_settings, file_secret_settings

            config_file_sources = []
            if "NLP_API_CONFIG_FILES" in os.environ:
                config_file_sources.extend([
                    _make_json_settings_source(pathlib.Path(p.strip()))
                    for p in os.getenv("NLP_API_CONFIG_FILES").split(",")
                ])

            return (*bases, *config_file_sources)


conf = Config()
