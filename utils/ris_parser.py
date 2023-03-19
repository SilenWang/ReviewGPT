import rispy
import pandas as pd
import io

class RisFileException(Exception):
    pass


class RisFile:
    '''
    ris文件解析器, 使用rispy模块
    '''
    def __init__(self, file):
        self.file = file
        self.fHandle = None


    def _fetch_info(self, kwd: list):
        collected = []
        for entry in rispy.load(self.fHanlde):
            rec = {}
            for key in kwd:
                if not key in self.keywords:
                    raise RisFileException(f'Not valid info that can be parsed from ris file, all keywords: {self.keywords}')
                rec[key] = entry[key]
            collected.append(rec)
        return pd.DataFrame(collected)


    def parse_info(self, kwd: list):
        '''
        解析给定区域的数值, 如果字段不存在则抛出错误
        '''
        if isinstance(self.file, str):
            with open(self.file, 'r') as self.fHanlde:
                return self._fetch_info(kwd)
        elif isinstance(self.file, io.StringIO):
            self.fHanlde = self.file
            return self._fetch_info(kwd)


    @property
    def keywords(self):
        '''
        调用rispy给出可解析的所有字段
        '''
        return set(rispy.TAG_KEY_MAPPING.values())


if __name__ == "__main__":
    risFile = RisFile(file='/home/silen/git_proj/ReviewGPT/test/G1/Paper035')
    print(risFile.keywords)
    print(risFile.parse_info(kwd=['doi', 'title', 'abstract']))
