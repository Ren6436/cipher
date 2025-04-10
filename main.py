from substitution_cipher import *
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import roman
import random


def get_text_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div", class_="forma proza")
    return content_div.get_text(separator="\n", strip=True) if content_div else ""


def clean_text(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace(' ', '_')
    return text.upper()


def download_krakatit(start_chapter=1, end_chapter=54, output_file="krakatit_cleaned.txt"):
    base_url = "https://cs.wikisource.org/wiki/Krakatit/"
    all_text = ""

    for chapter_num in range(start_chapter, end_chapter + 1):
        chapter_id = roman.toRoman(chapter_num)
        url = base_url + chapter_id + "."
        print(f"Fetching {url}")
        try:
            chapter_text = get_text_from_page(url)
            cleaned = clean_text(chapter_text)
            all_text += cleaned
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_text)
    print(f"\n Cleaned text saved to {output_file}")


if __name__ == "__main__":

    # download_krakatit()

    with open("krakatit_cleaned.txt", "r", encoding="utf-8") as f:
        krakatit_text = f.read()

    TM_ref = transition_matrix(get_bigrams(krakatit_text))

    with open("text_250_sample_1_ciphertext.txt", "r", encoding="utf-8") as f:
        ciphered = f.read().strip()

    found_key, cracked_text, score = prolom_substitute(ciphered, TM_ref, 20000)

    print("\n🔑 Recovered key:", found_key)
    print("📈 Plausibility score:", score)
    print("🔓 First 1000 characters of decrypted text:\n")
    print(cracked_text[:1000])
