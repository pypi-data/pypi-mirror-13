#!/usr/bin/python
# -*- encoding: utf-8 -*-

import inspect

def get_all_functions(func, prefix=None):
    all_func = inspect.getmembers(func, predicate=inspect.isfunction)
    if prefix: 
        return [k for k in all_func if k[0].startswith(prefix)]
    return all_func


_axes_func = {
    'tick_params':'tick_params',
    'title': 'set_title',
    'colorcycle': 'set_color_cycle',
    'grid': 'grid',
    'xbound': 'set_xbound',
    'xlabel': 'set_xlabel',
    'xlim': 'set_xlim',
    'xmargin': 'set_xmargin',
    'xscale': 'set_xscale',
    'xticklabels': 'set_xticklabels',
    'xticks': 'set_xticks',
    'ybound': 'set_ybound',
    'ylabel': 'set_ylabel',
    'ylim': 'set_ylim',
    'ymargin': 'set_ymargin',
    'yscale': 'set_yscale',
    'yticklabels': 'set_yticklabels',
    'yticks': 'set_yticks',
}

_axes_special_case = {
    # some methods are not possible with AxesSubplots
    'yminor': 'set_minor_locator',
    'ymajor': 'set_major_locator',
    'xminor': 'set_minor_locator',
    'xmajor': 'set_major_locator',
    'xminor_formatter': 'set_minor_formatter',
    'yminor_formatter': 'set_minor_formatter',
    'xmajor_formatter': 'set_major_formatter',
    'ymajor_formatter': 'set_major_formatter',
}

_figure_func = {
    'agg_filter': 'set_agg_filter',
    'alpha': 'set_alpha',
    'animated': 'set_animated',
    'axes': 'set_axes',
    'canvas': 'set_canvas',
    'clip_box': 'set_clip_box',
    'clip_on': 'set_clip_on',
    'clip_path': 'set_clip_path',
    'contains': 'set_contains',
    'dpi': 'set_dpi',
    'edgecolor': 'set_edgecolor',
    'facecolor': 'set_facecolor',
    'figheight': 'set_figheight',
    'figure': 'set_figure',
    'figwidth': 'set_figwidth',
    'frameon': 'set_frameon',
    'gid': 'set_gid',
    'label': 'set_label',
    'path_effects': 'set_path_effects',
    'picker': 'set_picker',
    'rasterized': 'set_rasterized',
    'size_inches': 'set_size_inches',
    'sketch_params': 'set_sketch_params',
    'snap': 'set_snap',
    'tight_layout': 'set_tight_layout',
    'transform': 'set_transform',
    'url': 'set_url',
    'visible': 'set_visible',
    'zorder': 'set_zorder',
}

_alias = {
    'lw': 'linewidth', 
    'ls': 'linestyle', 
    'mfc': 'markerfacecolor', 
    'mew': 'markeredgewidth', 
    'mec': 'markeredgecolor', 
    'ms': 'markersize',
    'mev': 'markevery', 
    'c': 'color', 
    'fs': 'fontsize',
    'cb': 'colorbar',
}

_plot_kwargs = {
    'aa': 'set_aa',
    'agg_filter': 'set_agg_filter',
    'alpha': 'set_alpha',
    'animated': 'set_animated',
    'antialiased': 'set_antialiased',
    'axes': 'set_axes',
    'c': 'set_c',
    'clip_box': 'set_clip_box',
    'clip_on': 'set_clip_on',
    'clip_path': 'set_clip_path',
    'color': 'set_color',
    'contains': 'set_contains',
    'dash_capstyle': 'set_dash_capstyle',
    'dash_joinstyle': 'set_dash_joinstyle',
    'dashes': 'set_dashes',
    'data': 'set_data',
    'drawstyle': 'set_drawstyle',
    'figure': 'set_figure',
    'fillstyle': 'set_fillstyle',
    'gid': 'set_gid',
    'label': 'set_label',
    'linestyle': 'set_linestyle',
    'linewidth': 'set_linewidth',
    'ls': 'set_ls',
    'lw': 'set_lw',
    'marker': 'set_marker',
    'markeredgecolor': 'set_markeredgecolor',
    'markeredgewidth': 'set_markeredgewidth',
    'markerfacecolor': 'set_markerfacecolor',
    'markerfacecoloralt': 'set_markerfacecoloralt',
    'markersize': 'set_markersize',
    'markevery': 'set_markevery',
    'mec': 'set_mec',
    'mew': 'set_mew',
    'mfc': 'set_mfc',
    'mfcalt': 'set_mfcalt',
    'ms': 'set_ms',
    'path_effects': 'set_path_effects',
    'picker': 'set_picker',
    'pickradius': 'set_pickradius',
    'rasterized': 'set_rasterized',
    'sketch_params': 'set_sketch_params',
    'snap': 'set_snap',
    'solid_capstyle': 'set_solid_capstyle',
    'solid_joinstyle': 'set_solid_joinstyle',
    'transform': 'set_transform',
    'url': 'set_url',
    'visible': 'set_visible',
    'xdata': 'set_xdata',
    'ydata': 'set_ydata',
    'zorder': 'set_zorder'
}

_contour_base = ['corner_mask','colors','alpha','cmap','norm','vmin','vmax',
                   'levels', 'extend', 'rasterized', 
                   'origin','extent','locator',
                   'extend','xunits','yunits','antialiased','nchunk',]
_contour_kwargs = _contour_base + ['linewidths','linestyles',]
_contourf_kwargs = _contour_base + ['hatches',]
_colorlabel_kwargs = ['inline','fontsize','fmt']
_colorbar_kwargs = ['shrink','pad','extendfrac','label']
_unique_params = ['label'] #will be deleted on each draw

# {k[4:]:k for k,v in get_all_functions(ax, 'set_<x,y>')}
# {k[4:]:k for k in dir(xxxxx) if k.startswith('set_')}
