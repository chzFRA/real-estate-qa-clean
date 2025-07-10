import os
import shutil
import requests
from bs4 import BeautifulSoup

def download_pdf_from_legislation(url, save_dir="pdfs"):
    """
    从 legislation.govt.nz 的指定页面上自动找到 .pdf 链接并下载到本地文件夹
    """
    # 构造一个“模拟浏览器”的Headers
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/114.0.0.0 Safari/537.36"
        )
    }

    # 请求网页
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"获取页面失败,HTTP状态码: {resp.status_code}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    pdf_link = None
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.endswith(".pdf"):
            pdf_link = href
            break

    if not pdf_link:
        print("页面上未找到任何PDF下载链接")
        return

    if pdf_link.startswith("/"):
        base_url = "https://www.legislation.govt.nz"
        pdf_link = base_url + pdf_link

    pdf_filename = pdf_link.split("/")[-1]
    save_path = os.path.join(save_dir, pdf_filename)

    print(f"正在下载: {pdf_link}")
    resp_pdf = requests.get(pdf_link, headers=headers, stream=True)
    if resp_pdf.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in resp_pdf.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"下载完成: {save_path}")
    else:
        print(f"下载失败,HTTP状态码: {resp_pdf.status_code}")


if __name__ == "__main__":
    # 每次运行前清空 pdfs 文件夹
    save_dir = "pdfs"
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    os.makedirs(save_dir)

    urls = [
        "https://www.legislation.govt.nz/act/public/2008/0066/latest/DLM1151921.html",
        "https://www.legislation.govt.nz/act/public/2008/0066/latest/DLM1151921.html?search=ts_act%40bill%40regulation%40deemedreg_Real+Estate+Agents+Act+2008_resel_25_a&p=1"
        "https://www.legislation.govt.nz/act/public/2004/0072/latest/DLM306036.html",
        "https://www.legislation.govt.nz/act/public/2011/0014/latest/DLM3366813.html",
        "https://www.legislation.govt.nz/act/public/2007/0097/latest/DLM1512301.html",
        "https://www.legislation.govt.nz/act/public/2002/0084/latest/DLM170873.html",
        "https://www.legislation.govt.nz/act/public/2005/0082/latest/DLM356881.html",
        "https://www.legislation.govt.nz/act/public/2020/0031/latest/LMS23223.html",
        "https://www.legislation.govt.nz/regulation/public/2012/0413/latest/DLM4932001.html",
        "https://www.legislation.govt.nz/act/public/1986/0120/latest/DLM94278.html",
        "https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM230265.html"
    ]

    for url in urls:
        download_pdf_from_legislation(url, save_dir=save_dir)