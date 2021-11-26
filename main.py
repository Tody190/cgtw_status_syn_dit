# -*- coding: utf-8 -*-
# author:yangtao
# time: 2021/11/25
"""
这个是一个 cgtw 事件触发脚本
本脚本在任务状态更改的时候触发
触发后会将指定阶段的任务状态传递给其它阶段任务状态
"""

import os
import pprint
import time
import sys

CGTW_ROOT_BIN = u"C:/CgTeamWork_v6.2/bin/"
# CGTW_ROOT_BIN = __file__.replace(u"\\", u"/").split(u"ext_plugin")[0]
for _path in [
    CGTW_ROOT_BIN + u"base",
    CGTW_ROOT_BIN + u"lib/pyside",
    CGTW_ROOT_BIN + u"cgtw",
    CGTW_ROOT_BIN + u"base/com_lib",
    CGTW_ROOT_BIN + u"base/com_icon"
]:
    _path in sys.path or sys.path.append(_path)

# cgtw
import cgtw2

t_tw = cgtw2.tw()


def task_fix_syn_dit():
    """

    :param src_pipeline:
    :param dst_pipeline:
    :return:
    """
    # 只处理任务模块的状态
    module_type = t_tw.client.get_module_type()
    module = t_tw.client.get_module()

    if not module == u"shot" or not module_type == u"task":
        return

    database = t_tw.client.get_database()
    task_id_list = t_tw.client.get_id()  # shot

    field_sign_list = [u"seq.entity",  # 场次
                       u"shot.entity",  # 镜头
                       u"pipeline.entity",  # 阶段
                       u"task.status",  # 状态
                       u"task.back_patch"]  # 回插状态

    # 获取当前任务的 场次， 镜头 ，阶段， 状态
    task_entity_list_info = t_tw.task.get(db=database,
                                          module=module,
                                          id_list=task_id_list,
                                          field_sign_list=field_sign_list)

    for task_info in task_entity_list_info:
        if not task_info.get(u"task.back_patch") == u"Y":  # 状态为回插镜头的才进行状态同步
            continue
        if not task_info.get(u"task.status") == u"返修":
            continue

        filter_list = [[u"seq.entity", u"=", task_info.get(u"seq.entity")],
                       u"and",
                       [u"shot.entity", u"=", task_info.get(u"shot.entity")],
                       u"and",
                       [u"pipeline.entity", u"=", u"dit"],
                       ]
        # 获取此环节的dit任务id
        dit_task_id_list = t_tw.task.get_id(db=database,
                                            module=module,
                                            filter_list=filter_list)

        if dit_task_id_list:
            # 修改状态
            t_tw.task.set(db=database,
                          module=module,
                          id_list=dit_task_id_list,
                          sign_data_dict={u"task.status": u"返修"})


if __name__ == u"__main__":
    task_fix_syn_dit()
