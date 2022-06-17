import time
import pandas
import os
import pandas.errors
from pandas import DataFrame

'''requirements:
pip install pandas
pip install xlsxwriter
pip install xlrd
pip install openpyxl
'''


class ExcelInitializer:
    def __init__(self):
        self.__file_path__ = 'url-validator-details.xlsx'
        self.__column_names__ = ['IndexCol', 'OriginalURL', 'CorrectedURL', 'CheckTime']
        self.__NewFile__()  # 新建表
        self.__InitializeColumn__()  # 初始化表

    def __NewFile__(self):
        """如果表不存在则新建"""
        if not os.path.exists(self.__file_path__):
            writer = pandas.ExcelWriter(self.__file_path__, engine='xlsxwriter')
            writer.save()

    def __InitializeColumn__(self):
        """初始化数据表"""
        # 读取数据表
        df_data = pandas.read_excel(self.__file_path__, sheet_name='Sheet1')
        # 循环查询数据表
        for column_name in self.__column_names__:
            # 检测当前列是否存在表中
            if column_name not in df_data.columns:
                # 新建一个列
                df_data[f'{column_name}'] = ''

        self.__SaveExcel__(data_frame=df_data)

    def __SaveExcel__(self, data_frame: DataFrame):
        data_frame.to_excel(self.__file_path__, sheet_name='Sheet1', index=False)

    def __read_index__(self):
        """获取当前数据表的最后序号"""
        df = pandas.read_excel(self.__file_path__, sheet_name='Sheet1', usecols=['IndexCol'])
        if df.empty:
            # print("空表")
            return 0
        else:
            tail = df.tail(1)  # 获取最后一行
            index = tail.iloc[0]['IndexCol']  # 获取最后一行的序号列的值
            # print(index)
            return index

    def DuplicateCheck(self, original_url, corrected_url):
        df = pandas.read_excel(self.__file_path__, sheet_name='Sheet1',
                               usecols=['IndexCol', 'OriginalURL', 'CorrectedURL'])
        print("检测重复")
        # 判断original_url所在行
        indexs_original_url = df.loc[df['OriginalURL'].str.contains(f'{original_url}', case=False, regex=False)][
            'IndexCol'].index
        if len(indexs_original_url > 0):
            # 判断corrected_url所在行
            indexs_corrected_url = \
                df.loc[df['CorrectedURL'].str.contains(f'{corrected_url}', case=False, regex=False, na=False)][
                    'IndexCol'].index
            if len(indexs_corrected_url > 0):
                # 是否取到IndexCol值
                # 取index实际值
                # 两表对比
                same_index = [index_original_url for index_original_url in indexs_original_url if
                              index_original_url in indexs_corrected_url]
                if len(same_index) > 0:
                    # 已经存在本行数据了
                    print("重复数据")
                    del df
                    return True
            del df
        return False

    def NewRow(self, original_url, corrected_url):

        if_is_duplicated = self.DuplicateCheck(original_url, corrected_url)

        if if_is_duplicated:
            return
        df_origin = pandas.read_excel(self.__file_path__, sheet_name='Sheet1')

        # 获取历史最后行数
        index = self.__read_index__()
        # 当前行数+1
        index += 1
        # 格式构造
        t = time.localtime()
        check_time = time.strftime("%H:%M:%S", t)
        data = {
            'IndexCol': [f"{index}"],
            'OriginalURL': [original_url],
            'CorrectedURL': [corrected_url],
            'CheckTime': [check_time],
        }
        print(f'数据插入完成{data}')
        # 生成数据表框架
        new_df = pandas.DataFrame(data)
        df_new = pandas.concat([df_origin, new_df], axis=0)  # 追加到原始数据后面 [表合并]
        # 保存表
        self.__SaveExcel__(data_frame=df_new)
        # 提示
        print(f'{data}/t 数据插入完成!')
        del df_origin
