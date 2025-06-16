
from anthropic_client import client
import requests
def extract_htlm(url):

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options


    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    html = driver.page_source

    driver.quit()
    return html

def extrate_images(urls):
    responses = []
    for url in urls:
        html = extract_htlm(url)

        responses.append(client.generate(
            messages=[
                {"role": "system", "content":"Only answer with URL link"},
                {"role": "user", "content": "from this HTML text, find the URL of the image of the product: " + html[:200000]}
            ]).content)
        
    return responses






