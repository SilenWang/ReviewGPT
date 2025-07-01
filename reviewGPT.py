from nicegui import ui
from datetime import datetime
from utils import task
import pandas as pd
import os

try:
    import utils.config as conf
except ImportError:
    import utils.config_sample as conf

# 全局状态
share_settings = {}
pdf_data = pd.DataFrame()
chat_history = []

def load_markdown(base):
    '''载入页面上的描述内容'''
    with open(f'lang/{base}.md') as f:
        return f.read()

def load_setting():
    '''将配置文件中的所有设置内容载入形成字典'''
    return {key: value for key, value in vars(conf).items() if not key.startswith("__")}

def run_review():
    '''触发进行文献阅读'''
    input_form = input_form_radio.value
    task_choice = task_choice_radio.value
    prompts = prompts_textarea.value
    pmids = pmids_textarea.value if input_form == 'PMID' else None
    ris_file = ris_file_upload.value if input_form == 'RIS File' else None
    
    paper_info = task.get_paper_info(input_form, share_settings['EMAIL'], pmids, ris_file)
    result = task.review(task_choice, paper_info, prompts, share_settings['OPENAI_KEY'], share_settings['REVIEW_MODEL'])
    output_markdown.content = result

def pdf_preprocess():
    '''PDF上传预处理'''
    pass
    # chat_history.append((None, 'File uploaded, now pre-processing, please do not ask question in paper mode until process is done'))
    # chat_display.refresh()

def pdf_process():
    '''处理PDF文件'''
    pass
    # global pdf_data
    # pdf_data = task.parse_pdf_info(pdf_file_upload.value, share_settings['OPENAI_KEY'])
    # pdf_postprocess()

def pdf_postprocess():
    '''PDF处理完成'''
    chat_history.append((None, 'PDF pre-process done, now you can ask question about this paper'))
    chat_display.refresh()

def send_message():
    '''处理用户消息'''
    message = message_input.value
    if not message:
        return
    
    chat_history.append((message, None))
    message_input.value = ''
    chat_display.refresh()
    
    # 获取回复
    mode = mode_radio.value
    if mode == 'Paper':
        reply = task.study(pdf_data, message, share_settings['OPENAI_KEY'], share_settings['REVIEW_MODEL'])
    else:
        reply = task.query(message, share_settings['OPENAI_KEY'], share_settings['REVIEW_MODEL'])
    
    chat_history[-1] = (message, reply)
    chat_display.refresh()

def clear_chat():
    '''清空聊天记录'''
    global chat_history
    chat_history = [(None, "Hi, I'm a bot to help you read papers, please first upload a pdf file in the left box")]
    chat_display.refresh()

def update_config():
    '''更新配置'''
    if openai_key_input.value:
        share_settings['OPENAI_KEY'] = openai_key_input.value
    if review_model_radio.value:
        share_settings['REVIEW_MODEL'] = review_model_radio.value
    if email_input.value:
        share_settings['EMAIL'] = email_input.value
    
    notice_label.text = f'Setting Updated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

# 初始化设置
share_settings = load_setting()

# 主界面
ui.markdown(load_markdown('Title'))


with ui.tabs() as tabs:
    review_tab = ui.tab('Review')
    study_tab = ui.tab('Study')
    setting_tab = ui.tab('Setting')

with ui.tab_panels(tabs, value=review_tab):
    # Review 标签页
    with ui.tab_panel(review_tab):
        ui.markdown(load_markdown('Review'))
        
        with ui.row():
            # 数据输入列
            with ui.column():
                ui.markdown('### Data Input')
                input_form_radio = ui.radio(['PMID', 'RIS File'], value='PMID').props('inline')
                pmids_textarea = ui.textarea(label='Input PMIDs').bind_visibility_from(input_form_radio, 'value', lambda x: x == 'PMID')
                ris_file_upload = ui.upload(label='Please Select RIS File', 
                                           auto_upload=True, 
                                           on_upload=lambda: None).bind_visibility_from(input_form_radio, 'value', lambda x: x == 'RIS File')
            
            # 任务设置列
            with ui.column():
                ui.markdown('### Task Setting')
                task_choice_radio = ui.radio(['Screen', 'Summarise'], value='Screen').props('inline')
                prompts_textarea = ui.textarea(label='Input Prompts')
        
        ui.button('REVIEW START', on_click=run_review)
        output_markdown = ui.markdown()
    
    # Study 标签页
    with ui.tab_panel(study_tab):
        ui.markdown(load_markdown('Study'))
        
        with ui.row():
            # 左侧控制面板
            with ui.column().classes('w-1/5'):
                pdf_file_upload = ui.upload(label='Please Select PDF File',
                                          auto_upload=True,
                                          on_upload=lambda: [pdf_preprocess(), pdf_process()])
                mode_radio = ui.radio(['Paper', 'Other'], value='Paper').props('inline')
                ui.button('Clear Dialog', on_click=clear_chat)
            
            # 右侧聊天区域
            with ui.column().classes('w-4/5'):
                @ui.refreshable
                def chat_display():
                    for msg in chat_history:
                        if msg[0]:
                            ui.chat_message(text=msg[0], name='User', sent=True)
                        if msg[1]:
                            ui.chat_message(text=msg[1], name='Bot', sent=False)
                
                chat_display()
                message_input = ui.input(label='Query').on('keydown.enter', send_message)
                ui.button('Send', on_click=send_message)
        
        # 初始化聊天记录
        clear_chat()
    
    # Setting 标签页
    with ui.tab_panel(setting_tab):
        ui.markdown(load_markdown('Setting'))
        
        with ui.card():
            ui.markdown('### OpenAI Setting')
            openai_key_input = ui.input(label='OpenAI API Key', value=share_settings.get('OPENAI_KEY', ''))
            review_model_radio = ui.radio(['gpt-3.5-turbo'], value=share_settings.get('REVIEW_MODEL', 'gpt-3.5-turbo')).props('inline')
        
        with ui.card():
            ui.markdown('### Pubmed API Setting')
            email_input = ui.input(label='Email', value=share_settings.get('EMAIL', ''))
        
        ui.button('Commit Setting', on_click=update_config)
        notice_label = ui.markdown()

ui.run(title='reviewGPT')
