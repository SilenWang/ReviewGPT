import pdfplumber
import pandas as pd
from openai.embeddings_utils import get_embedding
import openai

try:
    from utils.config import OPENAI_KEY
except ImportError:
    from utils.config_sample import OPENAI_KEY

class PdfFile:
    '''
    pdf文件解析器, 使用pdfplumber模块, 目前是个简单的实现, 之后需要找
    有没有什么更好的ML模块能更好的提取文章内容(精确到节段这种, embedding
    会更好), 决定位置也更精确
    '''

    def __init__(self, file, api_key=None):
        self.pdf_file = pdfplumber.open(file)
        self.api_key = api_key if api_key else OPENAI_KEY


    def __del__(self):
        if self.pdf_file:
            self.pdf_file.close()


    def parse_info(self):
        '''
        一页内容存一次, 所有内容通过模型进行预测
        '''
        all_text = []
        openai.api_key = self.api_key
        for page in self.pdf_file.pages:
            all_text.append({
                'page': page.page_number,
                'text': page.dedupe_chars().extract_text(layout=True)
            })
        text_data = pd.DataFrame(all_text)
        text_data['embedding'] = text_data['text'].apply(lambda x: get_embedding(x, engine='text-embedding-ada-002'))
        text_data.to_csv('debug.data.csv', index=0)
        return text_data


    @property
    def metadata(self):
        '''
        调用rispy给出可解析的所有字段
        '''
        return self.pdf_file.metadata


if __name__ == '__main__':
    pdf = PdfFile(file='/home/silen/git_proj/ReviewGPT/test/demo_paper.pdf')
    print(pdf.parse_info())
    