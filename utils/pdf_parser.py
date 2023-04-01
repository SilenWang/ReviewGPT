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
    1. pdf文件解析器, 目前使用pdfplumber模块简单实现
    2. 之后需要找更好的ML模块以能更好的提取文章内容(精确到节段), 位置定位更精确
    3. 在有新的提取方式以前, 这部分不添加设置项
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
        for page in self.pdf_file.pages:
            page_text = page.dedupe_chars().extract_text(layout=True)
            if page_text:
                all_text.append({
                    'page': page.page_number,
                    'text': page_text
                })
        text_data = pd.DataFrame(all_text)
        openai.api_key = self.api_key
        text_data['embedding'] = text_data['text'].apply(lambda x: get_embedding(x, engine='text-embedding-ada-002'))
        # text_data.to_csv('debug.data.csv', index=0)
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
    