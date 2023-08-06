#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from enum import Enum
import six

from odps.errors import DependencyNotInstalledError
from odps.df.expr.expressions import CollectionExpr, SequenceExpr, run_at_once
from odps.df.types import is_number


class PlottingCore(Enum):
    PANDAS = 'pandas'


def _plot_pandas(df, kind='line', **kwargs):
    x_label, y_label = kwargs.pop('xlabel', None), kwargs.pop('ylabel', None)

    x_label_size, y_label_size = kwargs.pop('xlabelsize', None), kwargs.pop('ylabelsize', None)
    label_size = kwargs.pop('labelsize', None)
    x_label_size = x_label_size or label_size
    y_label_size = y_label_size or label_size

    title_size = kwargs.pop('titlesize', None)

    annotate = kwargs.pop('annotate', None)
    x_annotate_scale = kwargs.pop('xannotatescale', 1.005)
    y_annotate_scale = kwargs.pop('yannotatescale', 1.005)

    fig = df.plot(kind=kind, **kwargs)

    import numpy as np
    if isinstance(fig, np.ndarray):
        figs = fig
        fig = fig[0]
    else:
        figs = [fig, ]

    if x_label:
        if x_label_size:
            fig.set_xlabel(x_label, fontsize=x_label_size)
        else:
            fig.set_xlabel(x_label)
    if y_label:
        if y_label_size:
            fig.set_ylabel(y_label, fontsize=y_label_size)
        else:
            fig.set_ylabel(y_label)

    if title_size:
        fig.title.set_fontsize(title_size)

    if annotate:
        for ax in figs:
            for p in ax.patches:
                ax.annotate(str(p.get_height()),
                            (p.get_x() * x_annotate_scale, p.get_height() * y_annotate_scale))

    return fig


def _hist_pandas(df, **kwargs):
    x_label, y_label = kwargs.pop('xlabel', None), kwargs.pop('ylabel', None)
    title = kwargs.pop('title', None)

    fig = df.hist(**kwargs)
    if x_label:
        fig.set_xlabel(x_label)
    if y_label:
        fig.set_ylabel(y_label)
    if title:
        fig.set_title(title)

    return fig


def _boxplot_pandas(df, **kwargs):
    x_label, y_label = kwargs.pop('xlabel', None), kwargs.pop('ylabel', None)
    title = kwargs.pop('title', None)

    fig = df.boxplot(**kwargs)
    if x_label:
        fig.set_xlabel(x_label)
    if y_label:
        fig.set_ylabel(y_label)
    if title:
        fig.set_title(title)

    return fig


@run_at_once
def _plot_sequence(expr, kind='line', use_cache=None, **kwargs):
    try:
        import pandas as pd
    except ImportError:
        raise DependencyNotInstalledError('plot requires for pandas')

    series = expr.to_pandas(use_cache=use_cache)
    xerr = kwargs.get('xerr', None)
    if xerr is not None and isinstance(xerr, (CollectionExpr, SequenceExpr)):
        kwargs['xerr'] = xerr.to_pandas()
    yerr = kwargs.get('yerr', None)
    if yerr is not None and isinstance(yerr, (CollectionExpr, SequenceExpr)):
        kwargs['yerr'] = yerr.to_pandas()
    return _plot_pandas(series, kind=kind, **kwargs)


@run_at_once
def _hist_sequence(expr, use_cache=None, **kwargs):
    try:
        import pandas as pd
    except ImportError:
        raise DependencyNotInstalledError('plot requires for pandas')

    series = expr.to_pandas(use_cache=use_cache)
    return _hist_pandas(series, **kwargs)


@run_at_once
def _plot_collection(expr, x=None, y=None, kind='line', use_cache=None, **kwargs):
    try:
        import pandas as pd
    except ImportError:
        raise DependencyNotInstalledError('plot requires for pandas')

    fields = []
    x_name = None
    y_name = None

    if x is not None:
        fields.append(x)
        if isinstance(x, six.string_types):
            x_name = x
        else:
            x_name = x.name
    if y is not None:
        fields.append(y)
        if isinstance(y, six.string_types):
            y_name = y
        else:
            y_name = y.name

    if x_name is None or y_name is None:
        for col in expr.dtypes.columns:
            if col.name == x_name or col.name == y_name:
                continue
            elif is_number(col.type):
                fields.append(col.name)

    if len(fields) != len(expr.dtypes):
        df = expr[fields].to_pandas()
    else:
        df = expr.to_pandas(use_cache=use_cache)

    if x_name is not None:
        kwargs['x'] = x_name
    if y is not None:
        kwargs['y'] = y_name

    xerr = kwargs.get('xerr', None)
    if xerr is not None and isinstance(xerr, (CollectionExpr, SequenceExpr)):
        kwargs['xerr'] = xerr.to_pandas()
    yerr = kwargs.get('yerr', None)
    if yerr is not None and isinstance(yerr, (CollectionExpr, SequenceExpr)):
        kwargs['yerr'] = yerr.to_pandas()

    return _plot_pandas(df, kind=kind, **kwargs)


@run_at_once
def _hist_collection(expr, use_cache=None, **kwargs):
    try:
        import pandas as pd
    except ImportError:
        raise DependencyNotInstalledError('plot requires for pandas')

    column = kwargs.get('column')
    if isinstance(column, six.string_types):
        column = [column, ]
    if column is not None:
        expr = expr[column]

    df = expr.to_pandas(use_cache=use_cache)

    return _hist_pandas(df, **kwargs)


@run_at_once
def _boxplot_collection(expr, use_cache=None, **kwargs):
    try:
        import pandas as pd
    except ImportError:
        raise DependencyNotInstalledError('plot requires for pandas')

    fields = set()

    column = kwargs.get('column')
    if isinstance(column, six.string_types):
        fields.add(column)
    elif column is not None:
        fields = fields.union(column)

    by = kwargs.get('by')
    if isinstance(by, six.string_types):
        fields.add(by)
    elif by is not None:
        fields = fields.union(by)

    if fields:
        expr = expr[list(fields)]

    df = expr.to_pandas(use_cache=use_cache)

    return _boxplot_pandas(df, **kwargs)


CollectionExpr.plot = _plot_collection
CollectionExpr.hist = _hist_collection
CollectionExpr.boxplot = _boxplot_collection
SequenceExpr.plot = _plot_sequence
SequenceExpr.hist = _hist_sequence

