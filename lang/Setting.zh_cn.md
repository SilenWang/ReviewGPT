### 设置说明

目前开放的设置项包括:

- `OpenAI API Key`: 目前所有的功能都基于OpenAI 提供的API实现, 所以该Key是必填项. 填写的Key不直接存储到本地, 而是在`gradio.States`对象中. 如果进行自部署, 则可以将内容写到`utils/config.py`文件中(参考`utils/config_sample.py`的格式)
- `Email`: 调用NCBI提供的API必须要提供邮箱, 因此也需要进行设置, 自部署的处理同`OpenAI API Key`