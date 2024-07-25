from attr_analyst.core.attr_calculator import generate_med_indexes
import pandas as pd

def test_generate_med_indexes():
    case_dict = {
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

    case_data = {
        'x1': [1, 2, 3],
        'x2': [4, 5, 6],
        'x3': [7, 8, 9],
        'x4': [1, 2, 3],
        'x5': [4, 5, 6],
        'x6': [4, 5, 6],
        'amt': [1, 2, 3],
        'store_name': ['a', 'b', 'c'],
        'category_name': ['a', 'b', 'c']
    }
    case_df = pd.DataFrame(case_data)
    relations_med, _ = generate_med_indexes(case_dict, case_df)

    assert relations_med == {

        "indexes": [
            {
                "indexes": ["x1", "x2"],
                "relation": "+",
                'med_indexes': ['x1', 'x2']
            },
            "x3",
            {
                "indexes": [
                    {
                        "indexes": ["x4", "x5"],
                        "relation": "*",
                        'med_indexes': ["x4", "x5"]
                    },
                    "x6"
                ],
                "med_indexes": [
                    "(x4 * x5)",
                    "x6"
                ],
                "relation": "+"
            }
        ],
        "med_indexes": [
            "(x1 + x2)",
            "x3",
            "((x4 * x5) + x6)"
        ],
        "relation": "*"

    }
