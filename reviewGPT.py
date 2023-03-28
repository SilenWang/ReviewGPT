import gradio as gr
from datetime import datetime
from utils import task

try:
    import utils.config as conf
except ImportError:
    import utils.config_sample as conf


# 定义
TITLE = "# ReviewGPT"
# 标题下的描述，支持md格式
DESCRIPTION = "ReviewGPT is an app that use the ChatGPT API to perform paper summarization and aggregation. My goal is to use AI to accelerate the reading and retrieval of papers."


def load_setting():
    '''
    将配置文件中的所有设置内容载入形成字典
    '''
    setting = {
        key: value for key, value in vars(conf).items() if not key.startswith("__")
    }
    return setting


# 构建Blocks上下文
with gr.Blocks() as reviewGPT:
    share_settings = gr.State(load_setting()) # 已经转换成字典了
    
    gr.Markdown(TITLE)
    gr.Markdown(DESCRIPTION)

    with gr.Tab("Review"):
        with gr.Row():       # 行排列
            with gr.Column():    # 列排列
                gr.Markdown('### Data Input')
                input_form = gr.Radio(
                    ["PMID", "RIS File"], value = "PMID", label="Select Input Form",
                )
                pmids = gr.Textbox(label="Input PMIDs", lines=9, visible=True, interactive=True)
                ris_file = gr.File(label="Please Select Ris File", visible=False, file_types=['.ris'], type='binary')
                # 不同选择时切换内容
                input_form.change(fn=lambda form: gr.update(visible=(form=='PMID')), inputs=input_form, outputs=pmids)
                input_form.change(fn=lambda form: gr.update(visible=(form=='RIS File')), inputs=input_form, outputs=ris_file)
            with gr.Column():    # 列排列
                gr.Markdown('### Task Setting')
                task_choice = gr.Radio(
                    ["Screen", "Summarise"], value = "Screen", label="Select a Task"
                )
                prompts = gr.Textbox(label="Input Prompts", lines=9, interactive=True)
        start = gr.Button(value='REVIEW START')
        out = gr.Markdown()

        def run_review(input_form, task_choice, prompts, pmids, ris_file, share_settings):
            '''
            click触发进行文献阅读
            '''
            paper_info = task.get_paper_info(input_form, share_settings['EMAIL'], pmids, ris_file)
            return task.review(task_choice, paper_info, prompts, share_settings['OPENAI_KEY'], share_settings['REVIEW_MODEL'])

        start.click(fn=run_review, inputs=[
            input_form, task_choice, prompts, pmids, ris_file, share_settings
        ], outputs=out)
    

    with gr.Tab("Study"): # 文献阅读页面用聊天机器人形式
        with gr.Row():
            with gr.Column(scale=0.2):
                pdf_file = gr.File(label="Please Select PDF File", visible=True, file_types=['.pdf'], type='binary')
                mode = gr.Radio(
                    ["Paper", 'Other'], value = "Paper", label="Query Mode", interactive=True
                )
                clear = gr.Button("Clear Dialog")

            with gr.Column(scale=0.8):
                chatbot = gr.Chatbot().style(height=350)
                with gr.Row():
                    msg = gr.Textbox(label='Query')

                def user(user_message, history):
                    return "", history + [[user_message, None]] # 第一个字段是输入框

                def bot(history, pdf_data, mode, share_settings):
                    question = history[-1][0]
                    if mode == 'Paper':
                        bot_message = task.study(pdf_data, question, share_settings['OPENAI_KEY'], share_settings['REVIEW_MODEL'])
                        history[-1][1] = bot_message # 将回复添加到最后
                    elif mode == 'Other':
                        bot_message = task.query(question, share_settings['OPENAI_KEY'], share_settings['REVIEW_MODEL'])
                        history[-1][1] = bot_message # 将回复添加到最后
                    else:
                        raise Exception('Invalid Query Mode')
                    return history

                msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                    bot, [chatbot, pdf_file, mode, share_settings], chatbot
                )
                clear.click(lambda: None, None, chatbot, queue=False)


    with gr.Tab("Setting"):

        # gr.Text('Model Selection(not effective now)')
        # model = gr.Textbox(label="Select a model", interactive=True)

        with gr.Box():
            gr.Markdown('### OpenAI Setting')
            openai_key = gr.Textbox(label='OpenAI API Key', value=None, interactive=True)
            review_model = gr.Radio(
                ["gpt-3.5-turbo"], value = "gpt-3.5-turbo", label="ChatGPT Version"
            )

        with gr.Box():
            gr.Markdown('### Pubmed API Setting')
            email = gr.Textbox(label='Email' , value=None, interactive=True)

        commit = gr.Button(value='Commit Setting')
        notice = gr.Markdown()

        # 虽然这个定义的位置比较奇怪, 但这是官方例子的写法...
        def update_config(openai_key: str, review_model: str, email: str, settings):
            '''
            其实之后应该有更好的更新写法?
            '''
            params = {k.upper(): v for k, v in locals().items() if (k != 'settings' and v != None)}
            settings.update(params)
            return {
                share_settings: settings,
                notice: f'Setting Updated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            }

        commit.click(
            fn=update_config,
            inputs=[openai_key, review_model, email, share_settings],
            outputs=[share_settings, notice]
        )



reviewGPT.launch()