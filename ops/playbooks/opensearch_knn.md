# ops/playbooks/opensearch_knn.md
1) ノードへ k-NN プラグイン導入: `./bin/opensearch-plugin install opensearch-knn`
2) 再起動後、`/_cat/plugins` で確認
3) インデックス作成（例）
{
"settings": {"index": {"knn": true}},
"mappings": {"properties": {"vec": {"type":"knn_vector", "dimension": 384}}}
}
4) 検索クエリ
{"size":5, "query":{"knn":{"vec":{"vector":[...], "k":5}}}}
