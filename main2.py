import tensorflow_hub as hub
import numpy as np

import tensorflow_text

model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")


def encode_sentences(sentences):
    embeddings = model(sentences)
    return np.array(embeddings).tolist()


def main(sentences):
    embeddings = encode_sentences(sentences)
    for i, embedding in enumerate(embeddings):
        print(f"Sentence: {sentences[i]}")
        print(f"Embedding: {embedding}\n")


if __name__ == "__main__":
    # Take sentences from command line arguments
    # sentences = ["特朗普当选美国总统 亚太伙伴们怎么看"]
    sentences = ["北京朝阳大悦城现砍人事件 警方通报嫌疑人被控制"]
    main(sentences)
