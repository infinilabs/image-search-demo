from os import listdir
from img2vec_pytorch import Img2Vec
from PIL import Image
from elasticsearch import Elasticsearch
import io

es = Elasticsearch(["http://localhost:9200"])


def convert_rgba_to_rgb(image_path):
    img = Image.open(image_path)

    if img.mode == "RGBA":
        img = img.convert("RGB")
        img.save(image_path)


def convert_rgba_to_rgb2(image_file):
    # Open the image file
    img = Image.open(image_file)

    # Check if the image is in RGBA mode
    if img.mode == "RGBA":
        # Convert the image to RGB mode
        img = img.convert("RGB")

        # Create a BytesIO object and save the image to it
        image_io = io.BytesIO()
        img.save(image_io, format="JPEG")

        # Seek to the beginning of the BytesIO object
        image_io.seek(0)

        return image_io

    return image_file


def main():
    img2vec = Img2Vec()

    arr = listdir("static/img")
    vectors = []

    es.indices.create(
        index="img-test",
        body={
            "settings": {"index.knn": True},
            "mappings": {
                "properties": {
                    "my_vec": {
                        "type": "knn_dense_float_vector",
                        "knn": {
                            "dims": 512,
                            "model": "lsh",
                            "similarity": "cosine",
                            "L": 99,
                            "k": 1,
                        },
                    }
                }
            },
        },
    )
    for img_path in arr:
        try:
            img = Image.open(f"static/img/{img_path}")
            vec = img2vec.get_vec(img, tensor=True)
            vec_np = vec.cpu().numpy().flatten().tolist()
            vectors.append(vec_np)
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

    for i, vec in enumerate(vectors):
        print(f"Vector for {arr[i]} is {vec}")
        document = {"title": arr[i], "my_vec": vec}
        es.index(index="img-test", body=document)


def vectorization(input):
    img2vec = Img2Vec()
    try:
        img = Image.open(input)
        vec = img2vec.get_vec(img, tensor=True)
        vec_np = vec.cpu().numpy().flatten().tolist()
        print(vec_np)
        return vec_np
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


if __name__ == "__main__":
    main()
    # convert_rgba_to_rgb("rabbit2.png")
    # vectorization("rabbit2.png")
