from attr_analyst.io import read_relation_config

def test_read_relation_config():
    test_path = 'tests/data/test_relation_config_file.json'
    assert read_relation_config(test_path) == {
        "label_column": "amt",
        "dimension_columns": ["store_name", "category_name"],
        "relations": {
            "indexes": [
                {
                    "indexes": ["x1", "x2"],
                    "relation": "+"
                },
                "x3",
                {
                    "indexes": [
                        {
                            "indexes": ["x4", "x5"],
                            "relation": "*"
                        },
                        "x6"
                    ],
                    "relation": "+"
                }
            ],
            "relation": "*"
        }
    }