import tensorflow_hub as hub
import numpy as np
from elasticsearch import Elasticsearch
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

import tensorflow_text

model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")

disable_warnings(InsecureRequestWarning)
es = Elasticsearch(["https://localhost:9200"], verify_certs=False, http_auth=('elastic', 'C+jwOFaytfIcaINu9cOS'))


def encode_sentences(sentences):
    embeddings = model(sentences)
    return np.array(embeddings).tolist()


def main(sentences):
    embeddings = encode_sentences(sentences)
    for i, embedding in enumerate(embeddings):
        print(f"Sentence: {sentences[i]}")
        print(f"Embedding: {embedding}\n")
        document = {
            "title": sentences[i],
            "title_vec": embedding
        }
        es.index(index="knn-test", body=document)


if __name__ == "__main__":
    sentences = ["马斯克：地球上的机器人数量终会超过人类，应重视对AI的监管",
                 "7年内超级AI将问世！OpenAI宣布：20%算力投入，4年内控制超级智能",
                 "考生走路甩手误将准考证扔河里 消防员跳河打捞",
                 "2024年美国总统大选：共和党参选人数上升， 选情趋白热化"]
    main(sentences)
