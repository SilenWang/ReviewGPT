from Bio import Entrez

try:
    from utils.config import EMAIL
except ImportError:
    from utils.config_sample import EMAIL


class PubMedFetcher:
    def __init__(self, email=None, pmids=None):
        self.email = email if email else EMAIL
        self.pmids = pmids


    def fetch_abstract(self):
        # 设置email和搜索关键词
        Entrez.email = self.email

        # 使用文章ID批量获取文章的题录和摘要信息
        handle = Entrez.efetch(db="pubmed", id=self.pmids, rettype="abstract", retmode="xml")
        fetch_record = Entrez.read(handle)

        # print(self.pmids)

        articles = []
        for idx, rec in enumerate(fetch_record["PubmedArticle"]):
            articles.append({
                'PMID': self.pmids[idx],
                'Title': rec["MedlineCitation"]["Article"]["ArticleTitle"],
                'Abstract': rec["MedlineCitation"]["Article"]["Abstract"]["AbstractText"][0] if "Abstract" in rec["MedlineCitation"]["Article"] else ""
            })

        return articles


if __name__ == '__main__':

    # 设置邮箱地址，提供给NCBI用于联系

    id_list = [26502953, 19016404, 25837277, 34209617, 35602107]

    fetcher = PubMedFetcher(email=EMAIL, pmids=id_list)

    print(fetcher.fetch_abstract())
