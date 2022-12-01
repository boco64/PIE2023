import abc
import pandas as pd
import torch

import pynance


class DatasetCreator(abc.ABC):
    torch_return_type = "torch"
    numpy_return_type = "numpy"
    def __init__(self, train_path=None, test_path=None) -> None:
        assert(any([train_path is not None, test_path is not None]))
        if(train_path is not None):
            assert(train_path.suffix==".csv")
        if(test_path is not None):
            assert(test_path.suffix==".csv")
        self._train_path = train_path
        self._test_path = test_path
    
    @abc.abstractmethod
    def get_train_sets(self, ratio, return_type):
        assert(return_type in [self.torch_return_type, self.numpy_return_type])
        assert(ratio > 0)
        assert(ratio <= 1)

    @abc.abstractmethod
    def get_test_set(self, return_type):
        assert(return_type in [self.torch_return_type, self.numpy_return_type])

    def read_csv(self):
        if(self._train_path is not None):
            self.train_df = self._read_csv(self._train_path)
        if(self._test_path is not None):
            self.test_df = self._read_csv(self._test_path)

    @abc.abstractmethod
    def _read_csv(self, path):
        pass


class StockValuePredictionDatasetCreator(DatasetCreator):
    def __init__(self, train_path=None, test_path=None) -> None:
        super().__init__(train_path, test_path)
        self.read_csv()

    def _read_csv(self, path):
        df = pd.read_csv(path, parse_dates=[pynance.utils.conventions.date_name])
        return df
        
    def get_train_sets(self, ratio, return_type, window):
        super().get_train_sets(ratio, return_type)
        data = self.train_df[pynance.utils.conventions.close_name].values
        train_length = int(len(data) * ratio)
        valid_length = len(data) - train_length

        if(return_type==self.torch_return_type):
            dataset = pynance.utils.datasets.torch.SlidingWindowDataset(data, window)            
            train_set, valid_set = torch.utils.data.random_split(dataset, (train_length, valid_length))
            return train_set, valid_set
        elif(return_type==self.numpy_return_type):
            print("Numpy return type remains to be done.")
            pass
            # TODO: depending on the model used behind, we don't necessarily want to create sliding windows...
            # we may just want to return the data, not even splited I believe
            # x, y = pynance.utils.transform.get_sliding_windows(data, window)
            # (x_train, y_train), (x_test, y_test) = 

    def get_test_set(self, return_type, window):
        super().get_test_set(return_type)
        data = self.test_df[pynance.utils.conventions.close_name].values
        if(return_type==self.torch_return_type):
            dataset = pynance.utils.datasets.torch.SlidingWindowDataset(data, window)            
            return dataset
        elif(return_type==self.numpy_return_type):
            print("Numpy return type remains to be done.")