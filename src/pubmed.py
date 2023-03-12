from Bio import Entrez
from config import EMAIL


class PubMedFetcher:
    def __init__(self, email, pmids):
        self.email = email
        self.pmids = pmids

    def fetch_abstract(self):
        # 设置email和搜索关键词
        Entrez.email = self.email

        # 使用文章ID批量获取文章的题录和摘要信息
        handle = Entrez.efetch(db="pubmed", id=id_list, rettype="abstract", retmode="xml")
        fetch_record = Entrez.read(handle)

        articles = []
        for i, rec in enumerate(fetch_record["PubmedArticle"]):
            articles.append({
                'PMID': id_list[i],
                'Title': rec["MedlineCitation"]["Article"]["ArticleTitle"],
                'Abstract': rec["MedlineCitation"]["Article"]["Abstract"]["AbstractText"][0] if "Abstract" in rec["MedlineCitation"]["Article"] else ""
            })

        return articles


if __name__ == '__main__':

    # 设置邮箱地址，提供给NCBI用于联系

    id_list = [26502953, 19016404, 25837277, 34209617, 35602107]

    fetcher = PubMedFetcher(email=EMAIL, pmids=id_list)

    print(fetcher.fetch_abstract())
