import h5py
import netCDF4


cache = dict()


class Dataset(object):
    """ Serializable cached h5py dataset

    Parameters
    ----------
    path: string
    datapath: string

    Examples
    --------
    >>> dset = H5PyDataset('myfile.hdf5', '/data/path/x')  # doctest: +SKIP
    >>> dset[0, :]  # doctest: +SKIP
    array([0, 1, 2])

    Holds an ``h5py.Dataset`` object directly

    >>> dset.dataset  # doctest: +SKIP
    <HDF5 dataset "/data/path/x": shape (5, 5), type "<i8">

    Serializes well

    >>> dset2 = pickle.loads(pickle.dumps(dset))  # doctest: +SKIP
    >>> dset2[0, :]  # doctest: +SKIP
    array([0, 1, 2])

    Caches dataset objects (and so limits the number of open files)

    >>> dset.dataset is dset2.dataset  # doctest: +SKIP
    True
    """
    @property
    def file(self):
        return self.dataset.file

    def isopen(self):
        return self.file.fid.valid

    @property
    def shape(self):
        return self.dataset.shape

    @property
    def dtype(self):
        return self.dataset.dtype

    @property
    def chunks(self):
        return self.dataset.chunks

    def __getitem__(self, key):
        return self.dataset[key]

    def __setitem__(self, key, value):
        self.dataset[key] = value

    def __getstate__(self):
        return self.path, self.datapath

    def __setstate__(self, state):
        self.__init__(*state)

class H5PyDataset(Dataset):
    def __init__(self, path, datapath):
        if (path, datapath) not in cache:
            f = h5py.File(path)
            cache[path, datapath] = f[datapath]
        if not cache[path, datapath].file.fid.valid:
            f = h5py.File(path)
            cache[path, datapath] = f[datapath]

        self.dataset = cache[path, datapath]
        self.path = path
        self.datapath = datapath


class NetCDFDataset(Dataset):
    def __init__(self, path, datapath):
        if (path, datapath) not in cache:
            f = netCDF4.Dataset(path)
            cache[path, datapath] = f.variables[datapath]
        if not cache[path, datapath].group().isopen():
            f = netCDF4.Dataset(path)
            cache[path, datapath] = f.variables[datapath]

        self.dataset = cache[path, datapath]
        self.path = path
        self.datapath = datapath

    def isopen(self):
        return self.dataset.group().isopen()
