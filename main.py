from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch
from img_vector import convert_rgba_to_rgb2, vectorization

app = Flask(__name__)


@app.route("/search", methods=["POST"])
def search_service():
    es = Elasticsearch("http://localhost:9200")

    # 获取表单数据
    index_name = request.form.get("index_name")  # 索引名

    # 获取上传的图片文件
    image_file = request.files.get("image")

    if not index_name or not image_file:
        return jsonify({"error": "Both index_name and image are required."}), 400

    # 处理图片
    image0 = convert_rgba_to_rgb2(image_file)
    vector_arr = vectorization(image0)

    if vector_arr is None:
        return jsonify({"error": "Error processing image."}), 400

    query_body = {
        "size": 10,
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
    # print(response["hits"]["hits"])
    results = response["hits"]["hits"]
    print(results)
    return render_template("search.html", results=results)

    # return jsonify(response)  # 返回搜索结果


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
