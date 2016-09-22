from __future__ import print_function
import numpy as np
import math
import os
from tabulate import tabulate
from scipy.optimize import curve_fit

def merge_data_arrays(array1,array2,res=0.065):
    '''
    Needs to be modified to work when one array equals overlap
    :param array1:
    :param array2:
    :param res:
    :return:
    '''
    first_is_left = array1[:, 0].min()<=array2[:, 0].min()
    l,r = {True:(array1,array2),False:(array2,array1)}[first_is_left]  #max(array1[:, 0].min(), array2[:, 0].min())
    overlap_idx1 = np.where((l[:, 0] >= r[:, 0].min()))
    #overlap_idx2 = np.where(np.logical_and((array2[:, 0] >= l), (array2[:, 0] <= r)))
    overlap_cnt = len(overlap_idx1[0])
    l_array, l_overlap = np.split(l,[-overlap_cnt],axis=0)
    r_overlap,r_array = np.split(r, [overlap_cnt], axis=0)
    weights = np.linspace(0,1,num=overlap_cnt)
    overlap = np.empty((overlap_cnt,2))
    overlap[:,0] = (l_overlap[:,0]+r_overlap[:,0])/2.0
    overlap[:,1] = l_overlap[:,1]*weights[::-1] + r_overlap[:, 1]*weights
    final = np.concatenate([x for x in (l_array,overlap,r_array) if len(x)],axis=0)

    return final


def subtract_data_arrays(array1,array2):
    if len(array1)==len(array2):
        result = np.empty_like(array1)
        result[:,0] = (array1[:,0]+array2[:,0])/2.0
        result[:,1] = array1[:,1]-array2[:,1]
        return result
    l = max(array1[:,0].min(),array2[:,0].min())
    r = min(array1[:,0].max(),array2[:,0].max())
    #first_is_left = array1[:, 0].min() <= array2[:, 0].min()
    #l, r = {True: (array1, array2), False: (array2, array1)}[first_is_left]
    overlap1 = array1[np.where(np.logical_and((array1[:,0] >= l),(array1[:,0] <= r)))]
    overlap2 = array2[np.where(np.logical_and((array2[:,0] >= l), (array2[:,0] <= r)))]
    result = np.empty_like(overlap1)
    overlap2 = np.resize(overlap2, overlap1.shape)
    result[:, 0] = (overlap1[:, 0] + overlap2[:, 0])/2.0
    result[:, 1] = overlap1[:, 1] - overlap2[:, 1]
    return result



def merge_spectrums(spectrum1,spectrum2,res=0.065):
    """

    :param spectrum1:
    :param spectrum2:
    :return:
    """

    spectrum1.em_wl = (min(spectrum1.em_wl[0],spectrum2.em_wl[0]),max(spectrum1.em_wl[1],spectrum2.em_wl[1]))
    spectrum1.signal = merge_data_arrays(spectrum1.norm_signal(), spectrum2.norm_signal(),res=res)
    if len(spectrum2.bg):
        spectrum1.bg = merge_data_arrays(spectrum1.norm_bg(), spectrum2.norm_bg(),res=res)
    if len(spectrum2.ref):
        spectrum1.ref = merge_data_arrays(spectrum1.norm_ref(), spectrum2.norm_ref(), res=res)
    spectrum1.frames = 1
    spectrum1.exposure = 1.0

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
        return np.array(data), sup
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


def bin_data_array(data,nbins=200):
    bins = np.array_split(data,nbins,axis=0)
    out = np.empty((nbins,2))
    for idx,bin in enumerate(bins):
        out[idx,0] = np.mean(bin[:,0])
        out[idx,1] = np.sum(bin[:,1])
    return out

def data_array_to_text_file(array,path,headers=None,table_fmt='plain',float_fmt='.2e',first_line=None):
    with open(path,'w') as f:
        if first_line is not None:
            print(first_line, file=f)
        print(tabulate(array,headers=headers,tablefmt=table_fmt,floatfmt=float_fmt),file=f)
        return path
    return None

def sum_of_gaussians(N):
    def gaussians(x,p):
        return np.sum([p['a'][i]*np.exp(-(x-p['mean'][i])**2/(2*p['sigma_sqr'][i])) for i in range(N)])

    return gaussians

def fit_sum_of_gaussians(x,f, ranges):
    res = np.mean(np.diff(x))
    y = f / res

    p0 = {'a':[], 'mean':[],'sigma_sqr':[]}

    gaussians = sum_of_gaussians(len(ranges))
    for mn,mx in ranges:
        p0['a'].append(np.where(np.logical_and(y<=mx,y>=mn),y,0.0).max() )
        p0['mean'].append( (mx+mn)/2.0 )
        p0['sigma_sqr'].append( mx-mn )
    try:
        p, pcov = curve_fit(gaussians, x, y, p0=p0)
    except:
        p = p0

        for key in p.keys():
            p[key] = [0.0]*len(ranges)
        pcov = 0.0
    return p, pcov

def integrate_gaussian(x,f):
    def gauss(x,a,mean,sigma_sqr):
        return a*np.exp(-(x-mean)**2/(2*sigma_sqr))

    res = np.mean(np.diff(x))
    y = f/res
    a0 = y.max()
    mean0 = np.sum(x * y) / np.sum(y)
    sigma_sqr0 = np.sqrt(np.sum(y * (x - mean0)**2) / np.sum(y))
    try:
        p, pcov = curve_fit(gauss, x, y, p0=[a0, mean0, sigma_sqr0])
    except:
        p = [0.0,0.0,0.0]
    return np.sqrt(2*np.pi*p[2])*p[0]

def pad_with_zeros(data, l,r):
    res = np.mean(np.diff(data[:,0]))
    min_wl = data[:,0].min()
    max_wl = data[:,0].max()
    add_l_wls = np.arange(l,min_wl,res)
    add_l = np.zeros((len(add_l_wls),2))
    add_l[:,0] = add_l_wls
    add_r_wls = np.arange(max_wl+res,r+res, res)
    add_r = np.zeros((len(add_r_wls),2))
    add_r[:, 0] = add_r_wls
    final = np.concatenate((add_l,data,add_r),axis=0)
    return final



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


