'''
这个文件里的所有内容其实应该精简以后全部放在ReviewerBot下
'''

from json import loads
import pandas as pd
import io

from utils.review  import Reviewer
from utils.pubmed  import PubMedFetcher
from utils.ris_parser  import RisFile
from utils.pdf_parser  import PdfFile


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


def review(task, paper_info, prompts, openai_key, review_model):
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
        papers = []
        for _, rec in paper_info.iterrows():
            if 'PMID' in rec:
                papers.append((rec['PMID'], rec['Abstract']))
            elif 'DOI' in rec:
                papers.append((rec['DOI'], rec['Abstract']))
            else:
                raise Exception('No PMID nor DOI in record.')
        response = reviewer.summarise(papers, prompts)
        return response['choices'][0]['message']['content']


def study(pdf_data, prompts, openai_key, review_model):
    reviewer = Reviewer(api_key=openai_key, model=review_model)
    fileHandle = io.BytesIO(pdf_data)
    pdf = PdfFile(file=fileHandle, api_key=openai_key)
    paper_data = pdf.parse_info()
    response = reviewer.study(prompts, paper_data)
    return response['choices'][0]['message']['content']


def query(prompts, openai_key, review_model):
    reviewer = Reviewer(api_key=openai_key, model=review_model)
    response = reviewer.query(prompts)
    return response['choices'][0]['message']['content']