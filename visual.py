import copy

import numpy as np
import visdom
import torch
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


'''
注意到，pca_for_dict和pca_dict两个函数会重复进行一些操作，所以还有改进的余地
'''


class VisObj:
    def __init__(self):
        self.epoch_idx = {}  # 每个窗口的横坐标画到了哪里，进行记录
        self.batch_losses = {}
        self.epoch_losses = {}
        self.vis = visdom.Visdom()
        self.pca_plot = pca_plot

    def add_epoch_loss(self, winname='epoch_losses', **loss_dict):
        if winname not in self.epoch_idx.keys():
            update = None
            self.epoch_idx[winname] = 1
        else:
            update = 'append'
            self.epoch_idx[winname] += 1
        ks, vs = self._dict2array(**loss_dict)
        self.vis.line(
            X=np.array([self.epoch_idx[winname]]),
            Y=vs, update=update, win=winname,
            opts={'title': winname, 'legend': ks}
        )

    @staticmethod
    def _dict2array(**loss_dict):
        ''' 将输入的一个个scale合并成visdom接受的array格式，并输出它和其名称 '''
        ks = []
        vs = []
        for k, v in loss_dict.items():
            ks.append(k)
            vs.append(v)
        vs = np.expand_dims(np.array(vs).squeeze(), 0)
        return ks, vs


def pca_for_dict(all_dict, ori=True, n_components=2, sub_qc_split=True):
    '''
    对all_dict中的original_x、recons_no_batch、recons_all进行pca，并返回为dict
    如果ori是False，则不对original进行pca，n_componets是pca的参数，sub_qc_split
    控制是返回整个数据集，还是将subject和qc分开返回。
    注意，没有被pca处理的all_dict中的部分，会原样返回。
    '''
    pca_dict = copy.deepcopy(all_dict)
    pca = PCA(n_components)
    if ori:
        # pca for original_x
        pca_dict['original_x'] = pca.fit_transform(all_dict['original_x'])
    # get reconstructed datas
    pca_dict['recons_no_batch'] = pca.fit_transform(
        all_dict['recons_no_batch'])
    pca_dict['recons_all'] = pca.fit_transform(all_dict['recons_all'])
    if sub_qc_split:
        qc_index = all_dict['ys'][:, -1] == 0
        sub_pca_dict = {k: v[~qc_index, :] for k, v in pca_dict.items()}
        qc_pca_dict = {k: v[qc_index, :] for k, v in pca_dict.items()}
        return sub_pca_dict, qc_pca_dict
    return pca_dict


def pca_plot(subject_pca, qc_pca):
    ''' 使用pca_for_dict得到的结果来绘制pca图 '''
    _, axs = plt.subplots(nrows=2, ncols=2, figsize=(14, 14))

    # Subject points of Original datas, reconstructed datas containing batch
    #   effects or no batch effects
    ax = axs[0, 0]
    ax.scatter(
        subject_pca['original_x'][:, 0], subject_pca['original_x'][:, 1],
        c='r', label='Original X', alpha=0.5
    )
    ax.scatter(
        subject_pca['recons_all'][:, 0], subject_pca['recons_all'][:, 1],
        c='b', label='Reconstructed X with BE', alpha=0.5
    )
    ax.scatter(
        subject_pca['recons_no_batch'][:, 0],
        subject_pca['recons_no_batch'][:, 1],
        c='g', label='Reconstructed X without BE', alpha=0.5
    )
    ax.set_title('Subject points')
    ax.legend()

    # QC points of Original datas, reconstructed datas containing batch
    #   effects or no batch effects
    ax = axs[0, 1]
    ax.scatter(
        qc_pca['original_x'][:, 0], qc_pca['original_x'][:, 1],
        c='r', label='Original X', alpha=0.5
    )
    ax.scatter(
        qc_pca['recons_all'][:, 0], qc_pca['recons_all'][:, 1],
        c='b', label='Reconstructed X with BE', alpha=0.5
    )
    ax.scatter(
        qc_pca['recons_no_batch'][:, 0],
        qc_pca['recons_no_batch'][:, 1],
        c='g', label='Reconstructed X without BE', alpha=0.5
    )
    ax.set_title('QC points')
    ax.legend()

    # reconstructed datas without batch effects of Subject points and QC points
    # Batch Label
    plot_index = np.any(subject_pca['ys'][:, 1] != -1)
    if plot_index:
        ax = axs[1, 0]
        ax.scatter(
            subject_pca['recons_no_batch'][:, 0],
            subject_pca['recons_no_batch'][:, 1],
            c=subject_pca['ys'][:, 1], label='Subject', alpha=0.1
        )
        scatter = ax.scatter(
            qc_pca['recons_no_batch'][:, 0],
            qc_pca['recons_no_batch'][:, 1],
            c=qc_pca['ys'][:, 1], label='QC', alpha=1.0
        )
        ax.set_title('Subject vs QC without BE under batch group')
        legend1 = ax.legend(
            *scatter.legend_elements(), loc="lower left", title='Batch')
        ax.add_artist(legend1)
        ax.legend()

    # reconstructed datas without batch effects of Subject points and QC points
    # injection order
    plot_index = np.any(subject_pca['ys'][:, 2] != -1)
    if plot_index:
        ax = axs[1, 1]
        ax.scatter(
            qc_pca['recons_no_batch'][:, 0], qc_pca['recons_no_batch'][:, 1],
            c='r', label='QC', alpha=0.5
        )
        scatter = ax.scatter(
            subject_pca['recons_no_batch'][:, 0],
            subject_pca['recons_no_batch'][:, 1],
            c=subject_pca['ys'][:, 2], label='Subject', alpha=0.5
        )
        ax.set_title('Subject vs QC without BE under predicted class')
        handles, labels = scatter.legend_elements()
        legend2 = ax.legend(
            *scatter.legend_elements(), loc="lower left", title='label')
        ax.add_artist(legend2)
        ax.legend()


def test():
    pass


if __name__ == '__main__':
    test()
