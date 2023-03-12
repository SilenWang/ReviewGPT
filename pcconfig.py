import pynecone as pc

config = pc.Config(
    app_name="ReviewGPT",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
