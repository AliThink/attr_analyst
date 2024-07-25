import copy
import json

import pandas as pd

def read_relation_config(config_file_path: str) -> dict:
    """
    读取指定文件路径的JSON配置文件内容，并返回一个字典对象。

    参数：
        config_file_path（str）：配置文件的文件路径。

    返回值：
        dict：解析后的JSON配置文件内容，以字典形式表示。
    """

    with open(config_file_path, "r") as file:
        config = json.load(file)
    
    return config

def generate_med_indexes(relations: dict, source_df: pd.DataFrame):
    relations_med = copy.deepcopy(relations)
    med_df = source_df.copy()
    
    def process_relation(data, df):
        if 'indexes' not in data or 'relation' not in data:
            return None
        
        indexes = data['indexes']
        relation = data['relation']
        med_indexes = []

        for idx in indexes:
            if isinstance(idx, dict):
                process_relation(idx, df)
                med_index = "({})".format(f' {idx["relation"]} '.join(idx['med_indexes']))
                df[med_index] = eval(f' {idx["relation"]} '.join([f'df["{col}"]' for col in idx['med_indexes']]))
                med_indexes.append(med_index)
            else:
                med_indexes.append(idx)

        # Compute the new column based on the relation and add it to the dataframe
        new_column_name = "({})".format(f' {relation} '.join(med_indexes))
        df[new_column_name] = eval(f' {relation} '.join([f'df["{col}"]' for col in med_indexes]))
        data['med_indexes'] = med_indexes

    process_relation(relations_med, med_df)
    
    return relations_med, med_df