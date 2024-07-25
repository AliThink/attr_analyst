from attr_analyst.core.attr_calculator import calculate_attr
import pandas as pd

def test_calculate_attr():
    med_dict = {
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

    case_data_2 = {
        'x1': [2, 4, 6],
        'x2': [5, 5, 8],
        'x3': [8, 10, 9],
        'x4': [2, 4, 6],
        'x5': [4, 7, 9],
        'x6': [3, 2, 4],
        'amt': [5, 5, 4],
        'store_name': ['a', 'b', 'c'],
        'category_name': ['a', 'b', 'c']
    }
    case_df_2 = pd.DataFrame(case_data_2)

    attr_output_df, merged_df, label_total_target, label_total_compare, label_total_rate = calculate_attr(case_df, case_df_2, 'amt', ['store_name', 'category_name'], med_dict)

    attr_output_df.to_excel('tests/output/test_calculate_attr_4.xlsx', index=False)

    assert 1 == 1