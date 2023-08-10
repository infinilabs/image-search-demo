# kNN demo

A handy example shows you how to search for vectors using the
[kNN plugin](https://www.infinilabs.com/docs/latest/easysearch/references/search/knn_api/) of
[Easysearch](https://www.infinilabs.com/products/easysearch/).

## Get started

Start an Easysearch instance:

```sh
# Make sure your vm.max_map_count meets the requirement
sudo sysctl -w vm.max_map_count=262144
docker run -it --rm -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e ES_JAVA_OPTS="-Xms512m -Xmx512m" \
  infinilabs/easysearch:1.3.0-24 \
  -E "security.enabled=false"
```

Install Python dependencies:

```sh
pip install -r requirements.txt
```

Start the server:

```sh
ES_SERVER=http://localhost:9200 python main.py
```

## ⚖️ License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or
  <http://www.apache.org/licenses/LICENSE-2.0>)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or <http://opensource.org/licenses/MIT>)

at your option.
