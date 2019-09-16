import os
import json
import time

import argparse
import torch.nn as nn
import torch.optim as optim


class NoneScheduler:
    def __init__(self, optimizer):
        pass

    def step(self):
        pass


class Config:

    sample_file = "./DATA/metabolic/sample.information.T3.csv"
    meta_file = "./DATA/metabolic/data_T3原始数据.csv"
    demo_sub_file = './DATA/Demo/sample.csv'
    demo_qc_file = './DATA/Demo/qc.csv'

    def __init__(self, pred=False):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '-s', '--save', default='./save',
            help='保存的文件夹路径，如果有重名，会在其后加-来区别'
        )
        self.parser.add_argument(
            '-d', '--data', default='metabolic',
            help="使用哪个数据，默认是metabolic，还可以是demo"
        )
        self.parser.add_argument(
            '-dn', '--data_norm', default='standard',
            help="数据正则化方式，默认是standard scale"
        )
        self.parser.add_argument(
            '-bs', '--batch_size', default=64, type=int,
            help='batch size，默认时64'
        )
        self.parser.add_argument(
            '-nw', '--num_workers', default=12, type=int,
            help='多进程数目，默认时12'
        )
        self.parser.add_argument(
            '-e', '--epoch', default=200, type=int,
            help='epoch 数量，默认是200'
        )
        self.parser.add_argument(
            '--bottle_num', type=int, default=100,
            help="瓶颈层的节点数量，默认是100"
        )
        self.parser.add_argument(
            '--no_batch_num', type=int, default=50,
            help="瓶颈层中不包含batch effect信息的节点数量，默认是50"
        )
        self.parser.add_argument(
            '--ae_disc_train_num', type=int, default=(1, 1), nargs=2,
            help="autoencode部分和discriminate部分训练次数的比例，默认是1:1"
        )
        self.parser.add_argument(
            '--ae_disc_lr', type=float, default=(0.001, 0.001), nargs=2,
            help=(
                "autoencode部分和discriminate部"
                "分训练时使用的lr，默认是0.001和0.001"
            )
        )
        self.parser.add_argument(
            '--ae_disc_weight', type=float, default=(1, 10), nargs=2,
            help="重建误差权重和对抗权重，默认是1.0和10.0"
        )
        self.parser.add_argument(
            '--supervise', default='both',
            help=(
                "用于discriminator的标签，如果是rank则"
                "只有排序，如果是cls则只有分类，如果是both则两者都有，默认是"
                "both"
            )
        )
        self.parser.add_argument(
            '--l2', default=0.0, type=float,
            help="weight decay, default 0.0"
        )
        self.parser.add_argument(
            '--label_smooth', default=0.2, type=float,
            help='label smoothing, default 0.2'
        )
        if pred:
            self.parser.add_argument(
                '-d', '--dir', help="想要预测的模型，指的是训练完保存的文件夹")
        self.args = self.parser.parse_args()

    def save(self, fname):
        self.save_dict = self.args.__dict__
        with open(fname, 'w') as f:
            json.dump(self.save_dict, f)

    def show(self):
        print('')
        print('此次训练使用的参数是：')
        for k, v in self.args.__dict__.items():
            print('%s:  %s' % (k, str(v)))
        print('')

