
filename = "./data/test_01.jsonl"

max_docs=256

end_points = {
    "local_geo" : {
        "url": 'http://localhost:5000/api/v1/annotators/SimpleTextGeographyAnnotator',
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "test 123"
        }
    }
}
