#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © %YEAR%  <>
#
# Distributed under terms of the %LICENSE% license.

"""

"""

import logging

logger = logging.getLogger(__name__)
import numpy as np
import argparse

import liver_model
import imtools
import body_navigation
import data_manipulation
import scipy


def automatic_liver_seeds(data3d, seeds, voxelsize_mm, fn_mdl='~/lisa_data/liver_intensity.Model.p'):
    from pysegbase import pycut
    # fn_mdl = op.expanduser(fn_mdl)
    mdl = pycut.Model({'mdl_stored_file':fn_mdl, 'fv_extern': liver_model.intensity_localization_fv})
    working_voxelsize_mm = np.asarray([4, 4, 4])

    data3dr = imtools.resize_to_mm(data3d, voxelsize_mm, working_voxelsize_mm)

    lik1 = mdl.likelihood_from_image(data3dr, working_voxelsize_mm, 0)
    lik2 = mdl.likelihood_from_image(data3dr, working_voxelsize_mm, 1)

    dl = lik2 - lik1

    seeds = add_negative_notrain_seeds(seeds,lik1, lik2)


    # Liver seed center

    # seed tam, kde je to nejpravděpodovnější - moc nefunguje
# escte jinak
    import scipy
    dst = scipy.ndimage.morphology.distance_transform_edt(dl>0)
    seed1 = np.unravel_index(np.argmax(dst), dst.shape)
    seed1_mm = seed1 * working_voxelsize_mm

    seed1z = seed1[0]


    add_negative_train_seeds_blobs(
        dl < 0,
        seeds,
        working_voxelsize_mm,
        voxelsize_mm,
        seed1z, n_seed_blob=2)

    seeds = data_manipulation.add_seeds_mm(
        seeds, voxelsize_mm,
        [seed1_mm[0]],
        [seed1_mm[1]],
        [seed1_mm[2]],
        label=1,
        radius=20,
        width=1
    )
    # import sed3
    # sed3.show_slices(data3dr, dl > 40.0, slice_step=10)
    return seeds


def add_negative_notrain_seeds(seeds,lik1, lik2, alpha=1.3):
    """

    :param seeds:
    :param lik1:
    :param lik2:
    :param alpha: 1.2 means 20% to liver likelihood
    :return:
    """
    # dl = 2*lik2 - lik1
    dl = (alpha*lik1-lik2)>0
    # for sure we take two iterations from segmentation
    # dl[0,:,:] = True
    # dl[:,0,:] = True
    # dl[:,:,0] = True
    # dl[-1,:,:] = True
    # dl[:,-1,:] = True
    # dl[:,:,-1] = True
    dl = scipy.ndimage.morphology.binary_erosion(dl, iterations=2, border_value=1)

    # and now i will take just thin surface
    dl_before=dl
    dl = scipy.ndimage.morphology.binary_erosion(dl, iterations=2, border_value=1)
    dl = imtools.qmisc.resize_to_shape((dl_before - dl) > 0, seeds.shape)
    seeds[dl>0] = 4

    return seeds

def add_negative_train_seeds_blobs(
        mask_working,
        seeds,
        working_voxelsize_mm,
        voxelsize_mm,
        seed1z, n_seed_blob=1):
    dll = mask_working

    # aby se pocitalo i od okraju obrazku
    dll[0,:,:] = 0
    dll[:,0,:] = 0
    dll[:,:,0] = 0
    dll[-1,:,:] = 0
    dll[:,-1,:] = 0
    dll[:,:,-1] = 0
    for i in range(0, n_seed_blob):

        dst = scipy.ndimage.morphology.distance_transform_edt(dll)
        # na nasem rezu
        dstslice = dst[seed1z, :, :]
        seed2xy = np.unravel_index(np.argmax(dstslice), dstslice.shape)
        # import PyQt4; PyQt4.QtCore.pyqtRemoveInputHook()
        # import ipdb; ipdb.set_trace()
        seed2 = np.array([seed1z, seed2xy[0], seed2xy[1]])
        seed2_mm = seed2 * working_voxelsize_mm

        seeds = data_manipulation.add_seeds_mm(
                seeds, voxelsize_mm,
                [seed2_mm[0]],
                [seed2_mm[1]],
                [seed2_mm[2]],
                label=2,
                radius=20,
                width=1
        )
        # for next iteration add hole where this blob is
        dll[seed1z, seed2xy[0], seed2xy[1]] = 0

def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        '-i', '--inputfile',
        default=None,
        required=True,
        help='input file'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        ch.setLevel(logging.DEBUG)


if __name__ == "__main__":
    main()