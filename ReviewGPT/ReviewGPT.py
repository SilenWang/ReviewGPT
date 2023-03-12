from turtle import width
from pcconfig import config
import pynecone as pc
from utils.review import Reviewer
from utils.pubmed import PubMedFetcher
from utils.config import EMAIL
from json import loads

docs_url = "https://pynecone.io/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


class State(pc.State):
    '''
    应用内部可变部分设置
    '''
    # 任务类型
    task: str = "Please Select Review Task"

    # 准入标准
    criterias: str = "Please Input Criterias"

    # 准入标准
    pmids: str = "Please Input PMIDs"

    # 解析结果
    output: str = 'Review Result'

    # 解析时的状态变量
    show: bool = False

    def change(self):
        self.show = not (self.show)

    def screen(self):
        '''
        调用已有函数进行文献工作:
        step1: 获取文献信息
        step2: 逐个文献判断是否符合准入标准 
        '''
        pmids = self.pmids.strip().split('\n')
        fetcher = PubMedFetcher(email=EMAIL, pmids=pmids)
        reviewer = Reviewer()

        answers = []
        for rec in fetcher.fetch_abstract():
            response = reviewer.screen(self.criterias, rec['Abstract'])
            answer = loads(response['choices'][0]['message']['content'])
            answers.append('\n'.join([
                f'### PMID: {rec["PMID"]}',
                f'- Title: {rec["Title"]}',
                f'- Inclusion: {answer["Inclusion"]}',
                '- Explanation:',
                '\n'.join([f'    + {exp}' for exp in answer["Explanation"]])
            ]))
        
        print(self.show)
        self.output = '\n\n------------------------\n\n'.join(answers)
        print(self.output)


def smallcaps(text, **kwargs):
    '''
    官方demo中的输出框文字
    '''
    return pc.text(
        text,
        font_size="0.7rem",
        font_weight="bold",
        text_transform="uppercase",
        letter_spacing="0.05rem",
        **kwargs,
    )


def header():
    "App的标题部分"
    return pc.box(
        pc.heading("Welcome to ReviewGPT", font_size="2em"),
        pc.text(
            "ReviewGPT is an app that use the ChatGPT model provided by OpenAI to perform paper summarization and aggregation. My goal is to use AI to accelerate the reading and retrieval of papers.",
            margin_top="0.5em",
            color="#666",
        ),
    )


def pmids():
    '''
    填写输入内容的方格, 用于pmids
    '''
    return pc.box(
        pc.text_area( # 获取文献的PMID
            placeholder="Please Input PMIDs",
            on_blur=State.set_pmids,
            margin_top="0.5rem",
            border_color="#eaeaef",
            width = "200%"
        ),
    )


def criterias():
    '''
    填写输入内容的方格, 用于pmids
    '''
    return pc.box(
        pc.text_area( # 获取文献的准入标准
            placeholder="Please Input Criterias",
            on_blur=State.set_criterias,
            margin_top="0.5rem",
            border_color="#eaeaef",
            width = "200%"
        ),
    )


def selection():
    '''
    官方demo中的输出框, 拿来放置任务选项
    '''
    return pc.box(
        pc.select(
            ['Screen', 'Summarise'],
            placeholder="Select a Task",
            on_change=State.set_task,
        ),
    )


def output():
    '''
    存放解析结果的文本框
    '''
    return pc.box(
        pc.box(
            smallcaps(
                "Review Result",
                color="#aeaeaf",
                background_color="white",
                padding_x="0.1rem",
            ),
            position="absolute",
            top="-0.5rem",
        ),
        pc.cond(
            State.show,
            pc.circular_progress(is_indeterminate=True),
            pc.markdown(State.output),
        ),
        padding="1rem",
        border="1px solid #eaeaef",
        margin_top="0.5rem",
        border_radius="8px",
        position="relative",
        width="70%"
    )


def index():
    '''
    应用首页, 提供:
    1. 一个功能选择按钮, 进行文章Review或者Screen
    2. 一个输入框, 可以输入文献ID
    3. 一个上传按钮, 可以上传RIS格式的文献题录(需要带摘要)
    4. 一个开始按钮, 开始进行文献解析
    '''
    return pc.center(
        pc.vstack(
            header(), # App标题
            selection(), # 任务选择框
            pmids(), # 需要被处理的文献编号
            criterias(), # 准入标准, 在总结时应当不需要显示
            pc.button("Screen", on_click=[State.change, State.screen, State.change], margin_top="0.5em"),
            output(),
            bg="white",
            padding="2em",
            shadow="lg",
            border_radius="lg",
            width="70%"
        ),
        width="100%",
        background="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%),radial-gradient(circle at 82% 25%,rgba(33,150,243,.18),hsla(0,0%,100%,0) 35%),radial-gradient(circle at 25% 61%,rgba(250, 128, 114, .28),hsla(0,0%,100%,0) 55%)",
    )


def about():
    '''
    项目介绍页面
    '''
    return pc.center(
        pc.vstack(
            pc.heading("About ReviewGPT", font_size="2em"),
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
