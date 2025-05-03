import os
from dotenv import load_dotenv

class Config:
    """
    Config class to load environment variables from a .env file.
    This class is used to manage configuration settings for the application.
    """

    #region OpenAI API Key
    __openai_api_key: str = None

    @property
    def openai_api_key(self) -> str:
        """
        Get the OpenAI API key from environment variables.
        :return: OpenAI API key.
        """
        if self.__openai_api_key is None:
            self.__openai_api_key = os.getenv("OPENAI_API_KEY")
        return self.__openai_api_key

    #endregion

    #region OpenAI GPT Model
    __openai_gpt_model: str = None
    @property
    def openai_gpt_model(self) -> str:
        """
        Get the OpenAI GPT model from environment variables.
        :return: OpenAI GPT model.
        """
        if self.__openai_gpt_model is None:
            self.__openai_gpt_model = os.getenv("GPT_MODEL")
        return self.__openai_gpt_model

    #endregion

    #region OpenAI O1 model
    __openai_o1_model: str = None

    @property
    def openai_o1_model(self) -> str:
        """
        Get the OpenAI O1 model from environment variables.
        :return: OpenAI O1 model.
        """
        if self.__openai_o1_model is None:
            self.__openai_o1_model = os.getenv("O1_MODEL")
        return self.__openai_o1_model
    #endregion

    #region Supabase API Key
    __supabase_api_key: str = None

    @property
    def supabase_api_key(self) -> str:
        """
        Get the Supabase API key from environment variables.
        :return: Supabase API key.
        """
        if self.__supabase_api_key is None:
            self.__supabase_api_key = os.getenv("SUPABASE_KEY")
        return self.__supabase_api_key

    #endregion

    #region Supabase URL
    __supabase_url: str = None

    @property
    def supabase_url(self) -> str:
        """
        Get the Supabase URL from environment variables.
        :return: Supabase URL.
        """
        if self.__supabase_url is None:
            self.__supabase_url = os.getenv("SUPABASE_URL")
        return self.__supabase_url
    #endregion

    def __init__(self):
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))