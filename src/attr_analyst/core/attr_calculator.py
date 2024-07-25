from attr_analyst.io import (
    generate_med_indexes,
    read_relation_config
)
import pandas as pd
import numpy as np

suffix_target = '_target'
suffix_compare = '_compare'
suffix_attr = '_c'
suffix_attr_origin = '_c_origin'
suffix_l = '_l'

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

def check_data_availibility(
    target_df: pd.DataFrame, 
    compare_df: pd.DataFrame, 
    label_column: str, 
    dimension_columns: list[str], 
):
    # Check if label_name exists in target_df and compare_df
    if label_column not in target_df.columns or label_column not in compare_df.columns:
        raise ValueError(f"label_column {label_column} not in target_df or compare_df")
    
    # Check if dimension_columns is included in both target_df and compare_df
    if not all(col in target_df.columns for col in dimension_columns) or not all(col in compare_df.columns for col in dimension_columns):
        raise ValueError(f"dimension_columns {dimension_columns} not in target_df or compare_df")
    
    # Check if the column names of target_df and compare_df are the same
    if target_df.columns.tolist()!= compare_df.columns.tolist():
        raise ValueError("target_df and compare_df have different column names")

def calculate_attr(
    target_df: pd.DataFrame, 
    compare_df: pd.DataFrame, 
    label_column: str, 
    dimension_columns: list[str], 
    relations: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, float, float, float] :

    check_data_availibility(target_df, compare_df, label_column, dimension_columns)

    relations_med, target_med_df = generate_med_indexes(relations, target_df)
    _, compare_med_df = generate_med_indexes(relations, compare_df)

    # 根据dimension_columns的值进行target与compare dataframe的join合并
    merged_df = pd.merge(target_med_df, compare_med_df, on=dimension_columns, how='outer', suffixes=(suffix_target, suffix_compare)).reset_index()
    merged_df.fillna(0.0000001, inplace=True)
    merged_df = merged_df.replace(0, 0.0000001)

    label_name_target = f"{label_column}{suffix_target}"
    label_name_compare = f"{label_column}{suffix_compare}"
    label_attr = f"{label_column}{suffix_attr}"
    
    # 2. 计算label_column的变化率
    label_total_target = merged_df[label_name_target].sum()
    label_total_compare = merged_df[label_name_compare].sum()
    label_total_rate = (label_total_target - label_total_compare) / label_total_compare

    # 3. 加法拆解label_clumn的总变化率到每一行
    merged_df[label_attr] = (merged_df[label_name_target] - merged_df[label_name_compare]) / label_total_compare
    gen_attr_result(relations_med, merged_df, label_column)

    attr_columns = gen_attr_columns(target_df, label_column, dimension_columns, label_attr)

    return merged_df[attr_columns], merged_df, label_total_target, label_total_compare, label_total_rate

def gen_attr_columns(target_df, label_column, dimension_columns, label_attr):
    attr_columns = dimension_columns + [label_attr]
    for index_column in target_df.columns:
        if index_column not in dimension_columns and index_column != label_column:
            attr_columns.append(f'{index_column}{suffix_attr}')

    return attr_columns

def gen_attr_result(
    relations: dict, 
    attr_df: pd.DataFrame, 
    label_name: str
): 
    if 'med_indexes' not in relations or 'indexes' not in relations or 'relation' not in relations:
        return None
    
    med_indexes = relations['med_indexes']
    indexes = relations['indexes']
    relation = relations['relation']

    cal_attr_relation(attr_df, med_indexes, relation, label_name)

    for index, idx in enumerate(indexes):
        if isinstance(idx, dict):
            gen_attr_result(idx, attr_df, med_indexes[index])


def cal_attr_relation(
    attr_df: pd.DataFrame, 
    med_indexes: list[any], 
    relation: str, 
    label_name: str
): 
    if relation == '+':
        # 加法归因
        cal_attr_plus(attr_df, med_indexes, label_name)
    elif relation == '*':
        # 乘法归因
        cal_attr_multiply(attr_df, med_indexes, label_name)
    else:
        raise ValueError(f"relation {relation} is not supported")


def attr_rerange(row, med_indexes: list[str], label_name: str):
    attr_total = sum([row[f'{med_index}{suffix_attr_origin}'] for med_index in med_indexes])

    attr_values = []
    for med_index in med_indexes:
        if attr_total == 0:
            attr_values.append(0)
        else:
            attr_ratio = row[f'{med_index}{suffix_attr_origin}'] / attr_total
            attr_values.append(attr_ratio * row[f'{label_name}{suffix_attr}'])

    return tuple(attr_values)

def cal_attr_plus(
    attr_df: pd.DataFrame, 
    med_indexes: list[any], 
    label_name: str
):
    ''' 加法归因 '''
    label_name_compare = f"{label_name}{suffix_compare}"

    for med_index in med_indexes:
        med_index_attr_origin = f"{med_index}{suffix_attr_origin}"
        med_index_target = f"{med_index}{suffix_target}"
        med_index_compare = f"{med_index}{suffix_compare}"

        attr_df[med_index_attr_origin] = (attr_df[med_index_target] - attr_df[med_index_compare]) / attr_df[label_name_compare]

    attr_df[[f'{med_index}{suffix_attr}' for med_index in med_indexes]] = attr_df.apply(attr_rerange, med_indexes=med_indexes, label_name=label_name, axis=1, result_type='expand')

def gen_label_l(row, label_name_target, label_name_compare):
    if row[label_name_target] == row[label_name_compare]:
        return 0
    else:
        return (row[label_name_target] - row[label_name_compare]) / (np.log(row[label_name_target]) - np.log(row[label_name_compare]))


def cal_attr_multiply(
    attr_df: pd.DataFrame, 
    med_indexes: list[any], 
    label_name: str
):
    ''' 乘法归因 '''
    label_name_target = f"{label_name}{suffix_target}"
    label_name_compare = f"{label_name}{suffix_compare}"
    label_l_name = f"{label_name}{suffix_l}"

    attr_df[label_l_name] = attr_df.apply(gen_label_l, label_name_target=label_name_target, label_name_compare=label_name_compare, axis=1)

    for med_index in med_indexes:
        med_index_attr = f"{med_index}{suffix_attr_origin}"
        med_index_target = f"{med_index}{suffix_target}"
        med_index_compare = f"{med_index}{suffix_compare}"

        attr_df[med_index_attr] = attr_df[label_l_name] * np.log(attr_df[med_index_target] / attr_df[med_index_compare]) / attr_df[label_name_compare]

    attr_df[[f'{med_index}{suffix_attr}' for med_index in med_indexes]] = attr_df.apply(attr_rerange, med_indexes=med_indexes, label_name=label_name, axis=1, result_type='expand')


