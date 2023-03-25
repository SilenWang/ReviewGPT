from utils.review import Reviewer
from utils.pubmed import PubMedFetcher
from utils.ris_parser import RisFile
from json import loads
import pandas as pd
import io


def get_paper_info(inputMethod, email=None, pmids=None, ris_data=None):
    '''
    解析文章信息准备用于解读
    '''

    if inputMethod == 'PMID':
        pmids = pmids.strip().split('\n')
        fetcher = PubMedFetcher(email=email, pmids=pmids)
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


def review_process(task, paper_info, prompts, openai_key, review_model):
    '''
    调用已有函数进行文献工作:
    1. 文献纳入判断(基于摘要)
    2. 文献小结(基于摘要)
    '''

    reviewer = Reviewer(api_key=openai_key, model=review_model)
    if task == 'Screen': # 准入任务
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


def review(
    inputMethod, task, prompts, pmids=None, risFile=None,
    email=None, openai_key=None, review_model=None
    ):
    '''
    review任务的函数:
    step1: 解析必要文件信息
    step2: 进行review
    '''
    paper_info = get_paper_info(inputMethod, email, pmids, risFile)
    return review_process(task, paper_info, prompts, openai_key, review_model)