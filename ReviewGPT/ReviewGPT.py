from pcconfig import config
import pynecone as pc
from utils.review import Reviewer
from utils.pubmed import PubMedFetcher
from utils.ris_parser import RisFile
from utils.config import EMAIL
from json import loads
import pandas as pd
import io


docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


class State(pc.State):
    '''
    应用内部可变部分设置
    '''
    # 任务类型
    inputMethod: str = "Please Select an Input Method"
    task: str = "Please Select Review Task"

    # 准入标准
    criterias: str = "Please Input Criterias"

    # 准入标准
    pmids: str = "Please Input PMIDs"

    # 解析结果
    output: str = 'No Review Result Yet'

    # 解析时的状态变量
    show_running: bool = False

    # 存储文章信息的数据框
    paper_info: pd.DataFrame = pd.DataFrame()

    # 用户上传的ris文件内容 // 这里使用bytes会报错, 应该是项目bug
    ris_data: str = ''

    upload_text: str = 'Drag and drop files here or click to select files'

    def change_run_status(self):
        self.show_running = not (self.show_running)


    async def handle_upload(self, file: pc.UploadFile):
        upload_data = await file.read()#.decode('utf-8')
        self.ris_data = upload_data.decode('utf-8')
        self.upload_text = f'Uploaded: {file.filename}'
    

    def get_paper_info(self):
        '''
        任务开始, 根据选择的task确定执行什么任务
        '''
        if self.task == 'Summarise':
            return

        if self.inputMethod == 'PMID':
            pmids = self.pmids.strip().split('\n')
            fetcher = PubMedFetcher(email=EMAIL, pmids=pmids)
            self.paper_info = pd.DataFrame(fetcher.fetch_abstract())
        elif self.inputMethod == 'RIS File':
            fileHandle = io.StringIO(self.ris_data)
            risFile = RisFile(file=fileHandle)
            self.paper_info = risFile.parse_info(kwd=['doi', 'title', 'abstract']).rename(columns={
                'doi': 'DOI',
                'title': 'Title',
                'abstract': 'Abstract'
            })


    def task_process(self):
        '''
        调用已有函数进行文献工作:

        State内不能Nested调用其他方法, 暂时不知道原因是什么

        1. 文献准入:
            step1: 获取文献信息
            step2: 逐个文献判断是否符合准入标准 
        2. 文献小结:
            pass
        '''
        if self.task == 'Screen': # 准入任务
            reviewer = Reviewer()
            answers = []
            for _, rec in self.paper_info.iterrows():
                response = reviewer.screen(self.criterias, rec['Abstract'])
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
            self.output = '\n\n------------------------\n\n'.join(answers)
        
        elif self.task == 'Summarise':
            self.output = 'Summarise Task Under Development Now'


def header():
    "App的标题部分"
    return pc.box(
        pc.heading("Welcome to ReviewGPT", size='lg'),
        pc.text(
            "ReviewGPT is an app that use the ChatGPT model provided by OpenAI to perform paper summarization and aggregation. My goal is to use AI to accelerate the reading and retrieval of papers.",
            margin_top="0.5em",
            color="#666",
        ),
        bg="white",
        padding="2em",
        shadow="lg",
        border_radius="lg",
    )


def task_region():
    '''
    任务设置区块:
    1. 选择任务类型
    2. 输入额外的任务要求(小节不需要, 准入需要)
    '''
    return pc.box(
        pc.heading("Task Setting", size='md'),
        pc.select(
            ['Screen', 'Summarise'],
            placeholder="Select a Task",
            on_change=State.set_task,
        ),
        pc.text_area( # 获取文献的准入标准
            placeholder="Please Input Criterias",
            on_blur=State.set_criterias,
            margin_top="0.5rem",
            border_color="#eaeaef",
            height = "150px"
        ),
        bg="white",
        padding="2em",
        shadow="lg",
        border_radius="lg",
        height = "300px",
        width = "400px",
    )


def input_region():
    '''
    输入设置区块:
    1. 选择PMID则出现输入框用于输入PMID
    2. 选择RIS File则出现文件上传框用于上传
    '''
    return pc.box(
        pc.heading("Data Input", size='md'),
        pc.select(
            ['PMID', 'RIS File'],
            placeholder="Select an Input Method",
            on_change=State.set_inputMethod,
        ),
        pc.cond(
            State.inputMethod == 'PMID',
            pc.text_area( # 获取文献的PMID
                placeholder="Please Input PMIDs",
                on_blur=State.set_pmids,
                margin_top="0.5rem",
                border_color="#eaeaef",
                height = "150px"
            ),
            pc.box()
        ),
        pc.cond(
            State.inputMethod == 'RIS File',
            pc.box(
                pc.upload(
                    pc.text(State.upload_text),
                    border="1px dotted rgb(107,99,246)",
                    padding="2em",
                    margin_top="0.5rem",
                    border_color="#eaeaef",
                    height = "100px"
                ),
                pc.button(
                    "Commit Upload",
                    margin_top="0.5em",
                    width = "350px",
                    on_click=lambda: State.handle_upload(
                        pc.upload_files()
                    ),
                )
            ),
            pc.box()
        ),
        bg="white",
        padding="2em",
        shadow="lg",
        border_radius="lg",
        height = "300px",
        width = "400px",
    )


def result_region():
    '''
    存放解析结果的文本框
    '''
    return pc.box(
        pc.button(
            "Review Start",
            on_click=[State.change_run_status, State.get_paper_info, State.task_process, State.change_run_status],
            margin_top="0.2em",
            width = "700px"
        ),
        pc.cond(
            State.show_running,
            pc.box(
                pc.heading("Reviewing", size='md'),
                pc.circular_progress(is_indeterminate=True),
            ),
            pc.box(
                pc.heading("Review Result", size='md'),
                pc.markdown(State.output),
            )
        ),
        bg="white",
        padding="2em",
        shadow="lg",
        border_radius="lg",
        width = "800px"
    )


def index():
    '''
    首页布局设置见项目内图片
    '''
    return pc.center(
        pc.vstack(
            header(), # App标题
            pc.hstack(
                pc.vstack(
                    input_region(),
                ),
                pc.vstack(
                    task_region(),
                ),
            ),
            result_region(),
            width="800px"
        ),
        height = "100%",
        background="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%),radial-gradient(circle at 82% 25%,rgba(33,150,243,.18),hsla(0,0%,100%,0) 35%),radial-gradient(circle at 25% 61%,rgba(250, 128, 114, .28),hsla(0,0%,100%,0) 55%)",
    )


def about():
    '''
    项目介绍页面
    '''
    return pc.center(
        pc.vstack(
            pc.heading("About ReviewGPT", size="lg"),
            pc.text(
                '''
                Researchers need to regularly summarize and categorize their published research results to understand 
                the current state of research and clarify future research directions. However, the fragmentation of 
                research results is more severe than that of Linux distributions, which I believe has to some extent 
                slowed down the pace of scientific research. Therefore, based on chtGPT, I build this app, hoping to 
                delegate the work of literature search and summarization to AI, so that we can quickly understand the 
                latest research results without relying on manually written reviews or systematic reviews.
                ''', 
                font_size="1.0em"
            ),
            spacing="1.5em",
            font_size="2em",
        ),
        padding_top="10%",
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.add_page(about)
app.compile()
