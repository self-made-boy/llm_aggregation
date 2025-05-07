import os
import re
import yaml
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv


class OpenAIConfig(BaseModel):
    api_key: Optional[str] = None
    api_base: str = "https://api.openai.com/v1"
    pxy_path_base: str = "/"
    child_keys: Optional[str] = None


class ClaudeBedrockConfig(BaseModel):
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    region: str = "us-east-1"
    event_types: list[str] = []
    model_mapping: dict[str, str]


class ClaudeConfig(BaseModel):
    api_key: Optional[str] = None
    auth_token: Optional[str] = None
    api_base: str = "https://api.anthropic.com/v1"
    proxy: Optional[str] = None
    pxy_path_base: str = "/"
    bedrock: ClaudeBedrockConfig


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False


class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    console: bool = True


class Settings(BaseModel):
    openai: OpenAIConfig
    claude: ClaudeConfig
    server: ServerConfig
    logging: LoggingConfig
    proxy_path_mapping: dict[str, str]


def load_settings() -> Settings:
    # 加载环境变量
    load_dotenv()

    # 默认配置文件路径
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yml")

    # 如果环境变量中指定了配置文件路径，则使用环境变量中的路径
    if os.environ.get("CONFIG_PATH"):
        config_path = os.environ.get("CONFIG_PATH")

    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    # 读取YAML配置文件
    with open(config_path, "r", encoding="utf-8") as f:
        yaml_content = f.read()

    # 替换环境变量
    pattern = r'\${([^}]+)}'

    def replace_env_vars(match):
        env_var = match.group(1)
        if ':-' in env_var:
            env_name, default_value = env_var.split(':-', 1)
            return os.environ.get(env_name, default_value)
        return os.environ.get(env_var, '')

    processed_yaml = re.sub(pattern, replace_env_vars, yaml_content)

    # 解析YAML
    config_data = yaml.safe_load(processed_yaml)

    # 将YAML配置转换为Settings对象
    return Settings(**config_data)


# 加载配置
settings = load_settings()
