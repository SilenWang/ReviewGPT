### Setting Instructions

The currently available setup options include:

- `OpenAI API Key`: All functionalities currently rely on the implementation of the OpenAI API, so this key is a required field. The filled-in key is not stored directly to the local machine, but instead in the `gradio.States` object. If self-deploying, you can write the content to the `utils/config.py` file (refer to the format of `utils/config_sample.py`), which can avoid having to fill in the key each time the page is refreshed.

- `Email`: To use the API provided by NCBI, an email address must be provided, so this setting is also required. The process for self-deployment is the same as that for the `OpenAI API Key`.
