import pynecone as pc

config = pc.Config(
    app_name="ReviewGPT",
    api_url="http://127.0.0.1:8000",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
