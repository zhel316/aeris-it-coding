from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    product_api_url: str = "https://tinyurl.com/2zp5p54a"

    auspost_api_key: str = "8ba91b84-ca46-40e6-9680-77e55e3c5942"
    auspost_password: str = "kE1Rt1ualfjjL2ESLLB4"
    auspost_account_number: str = "04456017"
    auspost_base_url: str = "https://digitalapi.auspost.com.au/test/shipping/v1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
