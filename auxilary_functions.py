import numpy as np
import math
import os



def wl_to_rgb(wl):
    select = np.select
    # power=np.power
    # transpose=np.transpose
    arange = np.arange

    def factor(wl):
        return select(
            [ wl > 700.,
              wl < 420.,
              True ],
            [ .3+.7*(780.-wl)/(780.-700.),
              .3+.7*(wl-380.)/(420.-380.),
              1.0 ] )

    def raw_r(wl):
        return select(
            [ wl >= 580.,
              wl >= 510.,
              wl >= 440.,
              wl >= 380.,
              True ],
            [ 1.0,
              (wl-510.)/(580.-510.),
              0.0,
              (wl-440.)/(380.-440.),
              0.0 ] )

    def raw_g(wl):
        return select(
            [ wl >= 645.,
              wl >= 580.,
              wl >= 490.,
              wl >= 440.,
              True ],
            [ 0.0,
              (wl-645.)/(580.-645.),
              1.0,
              (wl-440.)/(490.-440.),
              0.0 ] )

    def raw_b(wl):
        return select(
            [ wl >= 510.,
              wl >= 490.,
              wl >= 380.,
              True ],
            [ 0.0,
              (wl-510.)/(490.-510.),
              1.0,
              0.0 ] )

    gamma = 0.80
    def correct_r(wl):
        return math.pow(factor(wl)*raw_r(wl),gamma)
    def correct_g(wl):
        return math.pow(factor(wl)*raw_g(wl),gamma)
    def correct_b(wl):
        return math.pow(factor(wl)*raw_b(wl),gamma)


    return (correct_r(wl),correct_g(wl),correct_b(wl))


def color_map(wl):
    # ['r', 'g', 'b', 'y', 'g', 'k', 'm', 'c', 'k']
    col = 'b'
    if wl >485:
        col = 'c'
    if wl > 500:
        col = 'g'
    if wl > 565:
        col ='y'
    if wl > 590:
        col = 'm'
    if wl > 625:
        col = 'r'
    return col


def merge_data_arrays(array1,array2,res=0.065):
    l,r = round(max(min(array1[:,0]),min(array2[:,0])),ndigits=1 ), round(min(max(array1[:,0]),max(array2[:,0])), ndigits=1)
    idx1 = np.where(np.logical_and((array1[:,0] >= l),(array1[:,0] <= r)))
    idx2 = np.where(np.logical_and((array2[:,0] >= l), (array2[:,0] <= r)))
    avgd = []
    for wl1, sig1 in array1[idx1]:
        wl = wl1
        sig = sig1
        for wl2,sig2 in array2[idx2]:
            if abs(wl2-wl1)<res:
                wl = np.mean([wl1, wl2])
                sig = np.mean([sig1, sig2])
        avgd.append([wl,sig])
    overlap = np.asarray(avgd)
    idx1 = np.where(np.logical_or((array1[:, 0] < l), (array1[:, 0] > r)))
    idx2 = np.where(np.logical_or((array2[:, 0] < l), (array2[:, 0] > r)))
    first = array1[idx1]
    second = array2[idx2]
    final = np.vstack((first,second,overlap))
    return np.sort(final,axis=0)

def merge_spectrums(spectrum1,spectrum2,res=0.065):
    """

    :param spectrum1:
    :param spectrum2:
    :return:
    """

    spectrum1.em_wl = (min(spectrum1.em_wl[0],spectrum2.em_wl[0]),max(spectrum1.em_wl[1],spectrum2.em_wl[1]))
    spectrum1.signal = merge_data_arrays(spectrum1.signal, spectrum2.signal,res=res)
    if len(spectrum2.bg):
        spectrum1.bg = merge_data_arrays(spectrum1.bg, spectrum2.bg,res=res)
    if len(spectrum2.ref):
        spectrum1.ref = merge_data_arrays(spectrum1.ref, spectrum2.ref, res=res)
    return spectrum1


def merge_experiments(col1,col2):
    """

    :param col1:
    :param col2:
    :return:
    """
    col1.measurements.extend(col2.experiments)
    return col1


def read_ascii_file(path, file_del):
    data = []
    sup = []
    with open(path, 'r') as f:
        sig = True
        for line in f:
            if line in ['\n', '\r\n']:
                sig = False
                continue
            if sig:
                s = line.split(file_del)
                data.append([eval(s[0]), eval(s[1])])
            else:
                sup.append(line)
    if len(data):
        return data, sup
    return None

def organize_data(in_data,tags=('sig','bgd','ref'), ext='.asc'):
    '''
    :param data: Dictionary {file name: data array}
    :param data: text tags to organize by
    :return: Dictionarey {Name: {signal:array, bg:array, ref:array}
    '''

    out = {}
    for name, data in in_data.items():

        for tag in tags:

            if tag in name:
                if name.replace('_' + tag,'').replace(ext, '') in out.keys():
                    out[name.replace('_' + tag,'').replace(ext, '')][tag] = data
                else:
                    out[name.replace('_' + tag, '').replace(ext, '')] = {tag:data}
    return out

def import_group(path, names,delimiter=' '):
    dir_path = path
    data = {}
    for name in names:
        path = os.path.join(dir_path, name)
        if os.path.isfile(path):
            data[name] = read_ascii_file(path, delimiter)
    organized = organize_data(data)
    return organized

def import_folder(path,delimiter=' '):
    names = os.listdir(path)
    files = []
    for name in names:
        if os.path.isfile(os.path.join(path,name)):
            files.append(name)
    org_data = import_group(path,files,delimiter=delimiter)
    return org_data

def avg_data_array(data):
    all = {}
    final = {}
    for wl, sig in data:
        r_wl = round(wl,ndigits=1)
        if r_wl in all.keys():
            all[r_wl].append(sig)
        else:
            all[r_wl] = [sig]

    for wl, sigs in all.items():
        final[wl] = np.mean(sigs)
    return final

def bin_data_dict(data_dict):
    binned = {}

    for wl,sig in data_dict.items():
        r_wl = round(wl)
        if r_wl not in binned.keys():
            binned[r_wl] = sig
        binned[r_wl] += sig

    return binned



