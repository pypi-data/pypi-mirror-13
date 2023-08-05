# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import namedtuple

import numpy as np

from .common import generate_random_column_samples


InputData = namedtuple("InputData", [
    "X_original",
    "X_rescaled",
    "X_filled",
    "missing_mask",
    "column_means",
    "column_scales"
])


class Solver(object):
    def __init__(
            self,
            fill_method="zero",
            n_imputations=1,
            normalize_columns=False,
            min_value=None,
            max_value=None):
        self.fill_method = fill_method
        self.n_imputations = n_imputations
        self.normalize_columns = normalize_columns
        self.min_value = min_value
        self.max_value = max_value

    def _check_input(self, X):
        if len(X.shape) != 2:
            raise ValueError("Expected 2d matrix, got %s array" % (X.shape,))

    def _check_missing_value_mask(self, missing):
        if not missing.any():
            raise ValueError("Input matrix is not missing any values")
        if missing.all():
            raise ValueError("Input matrix must have some non-missing values")

    def _fill_columns_with_fn(self, X, missing_mask, col_fn):
        for col_idx in range(X.shape[1]):
            missing_col = missing_mask[:, col_idx]
            n_missing = missing_col.sum()
            if n_missing == 0:
                continue
            col_data = X[:, col_idx]
            fill_values = col_fn(col_data)
            X[missing_col, col_idx] = fill_values

    def fill(
            self,
            X,
            missing_mask,
            fill_method=None,
            inplace=False):
        """
        Parameters
        ----------
        X : np.array
            Data array containing NaN entries

        missing_mask : np.array
            Boolean array indicating where NaN entries are

        fill_method : str
            "zero": fill missing entries with zeros
            "mean": fill with column means
            "median" : fill with column medians
            "min": fill with min value per column
            "random": fill with gaussian samples according to mean/std of column

        inplace : bool
            Modify matrix or fill a copy
        """
        if not inplace:
            X = X.copy()

        if not fill_method:
            fill_method = self.fill_method

        if fill_method not in ("zero", "mean", "median", "min", "random"):
            raise ValueError("Invalid fill method: '%s'" % (fill_method))
        elif fill_method == "zero":
            # replace NaN's with 0
            X[missing_mask] = 0
        elif fill_method == "mean":
            self._fill_columns_with_fn(X, missing_mask, np.nanmean)
        elif fill_method == "median":
            self._fill_columns_with_fn(X, missing_mask, np.nanmedian)
        elif fill_method == "min":
            self._fill_columns_with_fn(X, missing_mask, np.nanmin)
        elif fill_method == "random":
            self._fill_columns_with_fn(
                X,
                missing_mask,
                col_fn=generate_random_column_samples)
        return X

    def prepare_input_data(self, X):
        """
        Check to make sure that the input matrix and its mask of missing
        values are valid. Returns X and missing mask.
        """
        X = np.asarray(X)
        if X.dtype != "f" and X.dtype != "d":
            X = X.astype(float)

        self._check_input(X)
        missing_mask = np.isnan(X)
        self._check_missing_value_mask(missing_mask)
        return X, missing_mask

    def biscale(self, X):
        """
        TODO: Implement iterative estimation of row and column centering/scaling
        parameters using the algorithm from page 31 of:
        Matrix Completion and Low-Rank SVD via Fast Alternating Least Squares

        row_center[i] =
            sum{j in observed[i, :]}{
                (1 / column_scale[j]) * (X[i, j] - column_center[j])
            }
            ------------------------------------------------------------
            sum{j in observed[i, :]}{1 / column_scale[j]}

        column_center[j] =
            sum{i in observed[:, j]}{
                (1 / row_scale[i]) * (X[i, j]) - row_center[i])
            }
            ------------------------------------------------------------
            sum{i in observed[:, j]}{1 / row_scale[i]}

        row_scale[i]**2 =
            mean{j in observed[i, :]}{
                (X[i, j] - row_center[i] - column_center[j]) ** 2
                --------------------------------------------------
                            column_scale[j] ** 2
            }

        column_scale[j] ** 2 =
            mean{i in observed[:, j]}{
                (X[i, j] - row_center[i] - column_center[j]) ** 2
                -------------------------------------------------
                            row_scale[i] ** 2
            }
        """
        raise ValueError("Bi-scaling not yet implemented")

    def normalize_input_matrix(self, X, inplace=False):
        if not inplace:
            X = X.copy()
        column_centers = np.nanmean(X, axis=0)
        column_scales = np.nanstd(X, axis=0)
        column_scales[column_scales == 0] = 1.0
        X -= column_centers
        X /= column_scales
        return X, column_centers, column_scales

    def project_result(
            self,
            X,
            column_centers=None,
            column_scales=None,
            row_centers=None,
            row_scales=None):
        """
        The solution matrices may be scaled or centered away from the range
        of actual values. Undo these transformations and clip values to
        fall within any global or column-wise min/max constraints.
        """
        X = np.asarray(X)
        n_rows, n_cols = X.shape
        if column_scales is not None:
            if len(column_scales) != n_cols:
                raise ValueError(
                    ("Expected vector of column scales to be %d elements, "
                     "got %d instead") % (
                        n_cols,
                        len(column_scales)))
            # broadcast the column scales across each
            X *= column_scales
        if row_scales is not None:
            if len(row_scales) != n_rows:
                raise ValueError(
                    ("Expected vector of row scales to have %d elements, "
                     "got %d instead") % (
                        n_rows,
                        len(row_scales)))
            X *= row_scales.reshape((n_rows, 1))

        if column_centers is not None:
            if len(column_centers) != n_cols:
                raise ValueError(
                    ("Expected vector of column centers to have %d elements, "
                     "got %d instead") % (
                        n_cols,
                        len(column_centers)))
            X += column_centers

        if row_centers is not None:
            if len(row_centers) != n_rows:
                raise ValueError(
                    ("Expected vector of row centers to have %d elements, "
                     "got %d instead") % (
                        n_rows,
                        len(row_centers)))
            X += row_centers.reshape((n_rows, 1))

        if self.min_value is not None:
            X[X < self.min_value] = self.min_value
        if self.max_value is not None:
            X[X > self.max_value] = self.max_value
        return X

    def solve(self, X, missing_mask):
        """
        Given an initialized matrix X and a mask of where its missing values
        had been, return a completion of X.
        """
        raise ValueError("%s.solve not yet implemented!" % (
            self.__class__.__name__,))

    def single_imputation(self, X):
        X_original, missing_mask = self.prepare_input_data(X)
        observed_mask = ~missing_mask
        X = X_original.copy()
        if self.normalize_columns:
            X, centers, scales = self.normalize_input_matrix(
                X,
                inplace=True)
        else:
            centers = scales = None
        X_filled = self.fill(X, missing_mask, inplace=True)
        if not isinstance(X_filled, np.ndarray):
            raise TypeError(
                "Expected %s.fill() to return NumPy array but got %s" % (
                    self.__class__.__name__,
                    type(X_filled)))

        X_result = self.solve(X_filled, missing_mask)
        if not isinstance(X_result, np.ndarray):
            raise TypeError(
                "Expected %s.solve() to return NumPy array but got %s" % (
                    self.__class__.__name__,
                    type(X_result)))

        X_result = self.project_result(
            X=X_result,
            column_centers=centers,
            column_scales=scales)
        X_result[observed_mask] = X_original[observed_mask]
        return X_result

    def multiple_imputations(self, X):
        """
        Generate multiple imputations of the same incomplete matrix
        """
        return [self.single_imputation(X) for _ in range(self.n_imputations)]

    def complete(self, X):
        """
        Expects 2d float matrix with NaN entries signifying missing values

        Returns completed matrix without any NaNs.
        """
        imputations = self.multiple_imputations(X)
        if len(imputations) == 1:
            return imputations[0]
        else:
            return np.mean(imputations, axis=0)
