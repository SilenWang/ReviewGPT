import gradio as gr
from datetime import datetime
from utils import task
import pandas as pd

try:
    import utils.config as conf
except ImportError:
    import utils.config_sample as conf


def load_markdown(base):
    '''
    载入页面上的描述内容
    '''
    with open(f'lang/{base}.md') as f:
        content = f.read()
    return content


def load_setting():
    '''
    将配置文件中的所有设置内容载入形成字典
    '''
    setting = {
        key: value for key, value in vars(conf).items() if not key.startswith("__")
    }
    return setting


def run_review(input_form, task_choice, prompts, pmids, ris_file, share_settings):
    '''
    click触发进行文献阅读
    '''
    paper_info = task.get_paper_info(input_form, share_settings['EMAIL'], pmids, ris_file)
    return task.review(task_choice, paper_info, prompts, share_settings['OPENAI_KEY'], share_settings['REVIEW_MODEL'])


def pdf_preprocess(history):
    '''
    解析pdf需要一定时间, 因此在对话框中显示
    提示用户先不要点击页面造成问题(强制措施过后写)
    '''
    return history + [[None, 'File uploaded, now pre-preocessing, please do not ask question in paper mode until process is done']] # 第一个字段是输入框


def pdf_process(pdf_data, share_settings):
    '''
    处理pdf文件为文章数据
    '''
    paper_data = task.parse_pdf_info(pdf_data, share_settings['OPENAI_KEY'])
    return paper_data
    

def pdf_postprocess(history):
    '''
    解析pdf需要一定时间, 因此在对话框中显示
    提示用户先不要点击页面造成问题(强制措施过后写)
    '''
    return history + [[None, 'PDF pre-preocess done, now you can ask question about this paper']] # 第一个字段是输入框


def user(user_message, history):
    '''
    处理输入框信息
    '''
    return "", history + [[user_message, None]] # 第一个字段是输入框


def bot(history, paper_data, mode, share_settings):
    '''
    根据输入框信息解析后返回处理结果
    '''
    question = history[-1][0]
    if mode == 'Paper':
        bot_message = task.study(paper_data, question, share_settings['OPENAI_KEY'], share_settings['REVIEW_MODEL'])
        history[-1][1] = bot_message # 将回复添加到最后
    elif mode == 'Other':
        bot_message = task.query(question, share_settings['OPENAI_KEY'], share_settings['REVIEW_MODEL'])
        history[-1][1] = bot_message # 将回复添加到最后
    else:
        raise Exception('Invalid Query Mode')
    return history


# 构建Blocks上下文
with gr.Blocks() as reviewGPT:
    share_settings = gr.State(load_setting()) # 已经转换成字典了
    pdf_data = gr.State(pd.DataFrame()) # PDF解析数据
    
    gr.Markdown(load_markdown('Title'))

    with gr.Tab("Review"):
        with gr.Box():
            gr.Markdown(load_markdown('Review'))
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

        start.click(fn=run_review, inputs=[
            input_form, task_choice, prompts, pmids, ris_file, share_settings
        ], outputs=out)
    

    with gr.Tab("Study"): # 文献阅读页面用聊天机器人形式
        ###### 布局部分 ######
        with gr.Box():
            gr.Markdown(load_markdown('Study'))
        with gr.Row():
            with gr.Column(scale=0.2):
                pdf_file = gr.File(label="Please Select PDF File", visible=True, file_types=['.pdf'], type='binary')
                mode = gr.Radio(
                    ["Paper", 'Other'], value = "Paper", label="Query Mode", interactive=True
                )
                clear = gr.Button("Clear Dialog")

            with gr.Column(scale=0.8):
                chatbot = gr.Chatbot(
                    value=[[None, "Hi, I'm a bot to help you read papers, please first upload a pdf file in the left box"]]
                ).style(height=350)
                with gr.Row():
                    msg = gr.Textbox(label='Query')
            
            ###### 响应部分 ######
            pdf_file.change(
                pdf_preprocess, chatbot, chatbot
            ).then(
                pdf_process, [pdf_file, share_settings], pdf_data
            ).then(
                pdf_postprocess, chatbot, chatbot
            )
            clear.click(lambda: None, None, chatbot, queue=False)
            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(# 这里的用于执行下一个动作
                bot, [chatbot, pdf_data, mode, share_settings], chatbot
            )


    with gr.Tab("Setting"):
        with gr.Box():
            gr.Markdown(load_markdown('Setting'))

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