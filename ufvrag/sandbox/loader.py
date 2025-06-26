import requests
import trafilatura
from bs4 import BeautifulSoup, SoupStrainer
from langchain.schema import Document
from langchain_community.document_loaders import WebBaseLoader


def load_lc() -> None:
    url = "https://wiki.dti.ufv.br/w/Guia_de_migra%C3%A7%C3%A3o_Java_EE_para_Jakarta_EE#Migra.C3.A7.C3.A3o_da_vers.C3.A3o_do_Java_usando_o_plugin_OpenRewrite"
    loader = WebBaseLoader(url)
    docs = loader.load()
    for doc in docs:
        print("----------------------------------")
        print(doc.page_content)


def load_bs() -> None:
    strainer = SoupStrainer("div", {"class": "main-content"})
    url = "https://wiki.dti.ufv.br/w/Guia_de_migra%C3%A7%C3%A3o_Java_EE_para_Jakarta_EE#Migra.C3.A7.C3.A3o_da_vers.C3.A3o_do_Java_usando_o_plugin_OpenRewrite"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser", parse_only=strainer)
    # for tag in soup(["nav", "footer", "script", "style"]):
    #     tag.decompose()

    text = soup.get_text(separator="\n")
    docs = [Document(page_content=text, metadata={"source": url})]
    for doc in docs:
        print("----------------------------------")
        print(doc.page_content)


def load_trafilatura() -> None:
    # url = 'https://wiki.dti.ufv.br/w/Guia_de_migra%C3%A7%C3%A3o_Java_EE_para_Jakarta_EE#Migra.C3.A7.C3.A3o_da_vers.C3.A3o_do_Java_usando_o_plugin_OpenRewrite'
    url = "https://wiki.dti.ufv.br/api.php?action=feedcontributions&user=Carrasco&feedformat=atom"
    downloaded = trafilatura.fetch_url(url)
    # text = trafilatura.extract(downloaded)
    text = trafilatura.extract(
        downloaded,
        include_formatting=True,
        include_links=False,  # opcional
        include_comments=False,  # opcional
    )
    if text is None:
        return
    docs = [Document(page_content=text, metadata={"source": url})]
    for doc in docs:
        print("----------------------------------")
        print(doc.page_content)


if __name__ == "__main__":
    load_trafilatura()
