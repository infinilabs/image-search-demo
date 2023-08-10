from PIL import Image
from elasticsearch import Elasticsearch
from flask import Flask, request, jsonify, render_template
from img2vec_pytorch import Img2Vec
import io
import os

DEFAULT_INDEX = "img-test"
app = Flask(__name__)
es = Elasticsearch(os.environ.get("ES_SERVER") or "http://localhost:9200")


def rgba2rgb(image_file):
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


def vectorize(input):
    img2vec = Img2Vec()
    try:
        img = Image.open(input)
        vec = img2vec.get_vec(img, tensor=True)
        vec_np = vec.cpu().numpy().flatten().tolist()
        return vec_np
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def init_indicies(index: str):
    if es.indices.exists(index):
        return
    # 初始化 kNN 索引
    print(f"Initializing {index}")
    es.indices.create(
        index,
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
    img_dir = "static/img"
    for title in os.listdir(img_dir):
        print(f"Indexing {title}")
        my_vec = vectorize(os.path.join(img_dir, title))
        body = {"title": title, "my_vec": my_vec}
        es.index(index=index, body=body)


@app.route("/search", methods=["POST"])
def search_service():
    # 获取表单数据
    index_name = request.form.get("index_name") or DEFAULT_INDEX  # 索引名

    # 获取上传的图片文件
    image_file = request.files.get("image")

    if not index_name or not image_file:
        return jsonify({"error": "Both index_name and image are required."}), 400

    # 处理图片
    image0 = rgba2rgb(image_file)
    vector_arr = vectorize(image0)

    if vector_arr is None:
        return jsonify({"error": "Error processing image."}), 400

    query_body = {
        "size": 50,
        "_source": "title",
        "query": {
            "bool": {
                "must": [
                    {
                        "knn_nearest_neighbors": {
                            "field": "my_vec",
                            "vec": {"values": vector_arr},
                            "model": "lsh",
                            "similarity": "cosine",
                            "candidates": 50,
                        }
                    }
                ]
            }
        },
    }

    if not index_name or not vector_arr:
        return jsonify({"error": "Both index_name and query are required."}), 400

    # 执行搜索
    response = es.search(index=index_name, body=query_body)

    # 使用模板显示搜索结果
    results = response["hits"]["hits"]
    print([r["_source"]["title"] for r in results], len(results))
    return render_template("search.html", results=results)


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


if __name__ == "__main__":
    init_indicies(DEFAULT_INDEX)
    app.run(port=5000, debug=True)
