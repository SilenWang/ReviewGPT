from utils.review import Reviewer
from utils.pubmed import PubMedFetcher
from utils.ris_parser import RisFile
from utils.config import EMAIL
from json import loads
import pandas as pd
import io
import gradio as gr


def get_paper_info(inputMethod, pmids=None, ris_data=None):
    '''
    解析文章信息准备用于解读
    '''

    if inputMethod == 'PMID':
        pmids = pmids.strip().split('\n')
        fetcher = PubMedFetcher(email=EMAIL, pmids=pmids)
        paper_info = pd.DataFrame(fetcher.fetch_abstract())
    elif inputMethod == 'RIS File':
        fileHandle = io.StringIO(ris_data.decode('utf-8'))
        risFile = RisFile(file=fileHandle)
        paper_info = risFile.parse_info(kwd=['doi', 'title', 'abstract']).rename(columns={
            'doi': 'DOI',
            'title': 'Title',
            'abstract': 'Abstract'
        })
    
    return paper_info


def task_process(task, paper_info, prompts):
    '''
    调用已有函数进行文献工作:
    1. 文献准入:
        step1: 获取文献信息
        step2: 逐个文献判断是否符合准入标准 
    2. 文献小结:
        pass
    '''

    if task == 'Screen': # 准入任务
        reviewer = Reviewer()
        answers = []
        for _, rec in paper_info.iterrows():
            response = reviewer.screen(prompts, rec['Abstract'])
            answer = loads(response['choices'][0]['message']['content'])
            if 'PMID' in rec:
                answers.append('\n'.join([
                    f'**PMID: {rec["PMID"]}**',
                    f'- Title: {rec["Title"]}',
                    f'- Inclusion: {answer["Inclusion"]}',
                    '- Explanation:',
                    '\n'.join([f'    + {exp}' for exp in answer["Explanation"]])
                ]))
            elif 'DOI' in rec:
                answers.append('\n'.join([
                    f'**DOI: {rec["DOI"]}**',
                    f'- Title: {rec["Title"]}',
                    f'- Inclusion: {answer["Inclusion"]}',
                    '- Explanation:',
                    '\n'.join([f'    + {exp}' for exp in answer["Explanation"]])
                ]))
            else:
                raise Exception('No PMID nor DOI in record.')
        return '\n\n------------------------\n\n'.join(answers)
    
    elif task == 'Summarise':
        return 'Summarise Task Under Development Now'


# async def handle_upload(self, file: pc.UploadFile):
#     upload_data = await file.read()#.decode('utf-8')
#     self.ris_data = upload_data.decode('utf-8')


def run(inputMethod, task, prompts, pmids=None, risFile=None):
    '''
    运行函数
    '''
    paper_info = get_paper_info(inputMethod, pmids, risFile)
    return task_process(task, paper_info, prompts)


# 定义
TITLE = "# ReviewGPT"
# 标题下的描述，支持md格式
DESCRIPTION = "ReviewGPT is an app that use the ChatGPT API to perform paper summarization and aggregation. My goal is to use AI to accelerate the reading and retrieval of papers."

# 构建Blocks上下文
with gr.Blocks() as reviewGPT:
    gr.Markdown(TITLE)
    gr.Markdown(DESCRIPTION)
    with gr.Row():       # 行排列
        with gr.Column():    # 列排列
            gr.Markdown('### Data Input')
            inputForm = gr.Radio(
                ["PMID", "RIS File"], label="Select Input Form"
            )
            pmids = gr.Textbox(label="Input PMIDs", lines=9, visible=True, interactive=True)
            risFile = gr.File(label="Please Select Ris File", visible=False, file_types=['.ris'], type='binary')
            # 不同选择时切换内容
            inputForm.change(fn=lambda form: gr.update(visible=(form=='PMID')), inputs=inputForm, outputs=pmids)
            inputForm.change(fn=lambda form: gr.update(visible=(form=='RIS File')), inputs=inputForm, outputs=risFile)
        with gr.Column():    # 列排列
            gr.Markdown('### Task Setting')
            task = gr.Radio(
                ["Screen", "Summarise"], label="Select a Task"
            )
            prompts = gr.Textbox(label="Input Prompts", lines=9, interactive=True)
    start = gr.Button(label=['REVIEW START'])
    out = gr.Markdown(label='Review Result')

    start.click(fn=run, inputs=[inputForm, task, prompts, pmids, risFile], outputs=out)

reviewGPT.launch()