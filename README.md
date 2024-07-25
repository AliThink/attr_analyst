# attr_analyst

[attr_analyst] Attributing changes in target metrics to related metrics and calculating the contribution values of the related metrics.

## Main Features

1. **Flexible relationship configuration**: Support for complex nested attribution relationship configuration via configuration files.
2. **Support multiple attribution models**: Allow for the free combination of additive and multiplicative attribution models.
3. **Output of attribution process and results**: Provide output of intermediate attribution results for flexible application of hierarchical attribution results.

## Where to get it

```sh
# PyPI
pip install attr_analyst
```

## Example

### 1. Prepare a json file for relation config.
```json
/* test_relation_config_file.json

Attribution target index: amt
The final result of attribution is to attribute the change value of the target index to the contribution of the change in the related index.

Attribution dimension index: store_name, category_name 
According to these index values, perform data association between the current DataFrame and the comparative DataFrame to calculate the change value.

Attribution related index: x1, x2, x3, x4, x5, x6
*/
{
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
```

### 2. Prepare the data source and call the corresponding method to complete the attribution operation.
> target_df and compare_df should have the same column names and quantities.

```python
# Explanation of core methods

def calculate_attr_from_config(
    target_df: pd.DataFrame,
    compare_df: pd.DataFrame,
    relation_config_path: str
) -> tuple[pd.DataFrame, pd.DataFrame, float, float, float] :
    """
    Calculates the attributes between the target DataFrame and the comparison DataFrame according to the configuration file.

    Parameters:
        target_df (pd.DataFrame): The target DataFrame.
        compare_df (pd.DataFrame): The comparison DataFrame.
        relation_config_path (str): The path of the relationship configuration file.

    Returns:
        tuple: A tuple containing the following:
            - attr_output_df (pd.DataFrame): A DataFrame containing the final attribution calculation results, with the suffix "_c" for the corresponding index attribution results.
            - attr_progress_df (pd.DataFrame): A DataFrame containing the attribution results of the intermediate calculation process.
            - label_total_target (float): The total result of the attribution target in the current period.
            - label_total_compare (float): The total result of the attribution target in the comparison period.
            - label_total_rate (float): The rate of change of the attribution target.

    """
    
    relation_config = read_relation_config(relation_config_path)
    label_column = relation_config['label_column']
    dimension_columns = relation_config['dimension_columns']
    relations = relation_config['relations']

    return calculate_attr(target_df, compare_df, label_column, dimension_columns, relations)

```


```python
from attr_analyst import calculate_attr_from_config
import pandas as pd

relation_config_filepath = 'test_relation_config_file.json'

target_data = {
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
target_df = pd.DataFrame(target_data)

compare_data = {
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
compare_df = pd.DataFrame(compare_data)

attr_output_df, attr_progress_df, label_total_target, label_total_compare, label_total_rate = calculate_attr_from_config(target_df, compare_df, relation_config_filepath)

attr_output_df.to_excel('test_calculate_attr_from_config_output.xlsx', index=False)

```
