#!/usr/bin/python
# -*- encoding: utf-8 -*-

from justplot import util
import matplotlib as mpl
import matplotlib.pyplot as plt

class JustPlot(object):
    kwarg_defaults = {
        'fig': None,
        'ax': None,
        'figsize': None,
        'dpi': mpl.rcParams['figure.dpi'],
        'subplots':False,
        'sharex':False,
        'sharey':False,
    }

    def __init__(self, *args, **kwargs):
        self.zlayer = []
        self.zlayer_kwargs = []
        self.args = []
        self.newargs = False
        self.kwargs = self.kwarg_defaults.copy()
        self.setup(*args, **kwargs)
 
    def __call__(self, *args, **kwargs):
        self.setup(*args, **kwargs)   

    def setup(self, *args, **kwargs):
        self._update(*args, **kwargs)
        
        if not self.kwargs.get('fig', False):
            if self.kwargs.get('subplots'):
                self._create_fig_and_axes_subplots()
            else:
                self._create_fig_and_axes()
        
        self._setup_ax()
        self._setup_fig()

    def add_plot(self,*args, **kwargs):
        plot_kwargs = self._get_allowed_values(util._plot_kwargs, source=kwargs)
        pl = self.kwargs['ax'].plot(*args, **kwargs)
        
    def add_contourf(self, *args, **kwargs):
        contourf_kwargs = self._get_allowed_values(util._contourf_kwargs, source=kwargs)
        con = self.kwargs['ax'].contourf(*args, **contourf_kwargs)
        #self.zlayer.append(con)
        #self.zlayer_kwargs.append(kwargs)
        if kwargs.get('colorbar', False):
            cbar_kwargs = self._get_allowed_values(util._colorbar_kwargs, source = kwargs)
            self.kwargs['fig'].colorbar(con, ax=self.kwargs['ax'], **cbar_kwargs)

    def add_contour(self, *args, **kwargs):
        contour_kwargs = self._get_allowed_values(util._contour_kwargs, source=kwargs)
        con = self.kwargs['ax'].contour(*args, **kwargs)
        if kwargs.get('colorlabel', False):
            clab_kwargs = self._get_allowed_values(util._colorlabel_kwargs, source=kwargs)
            plt.clabel(con, **clab_kwargs)
            #self.kwargs['fig'].clabel(con, **clab_kwargs)
    
    def add_legend(self, *args, **kwargs):
        self.kwargs['ax'].legend(*args, **kwargs)
   
    def reset(self, hard=False):
        self.args = []
        self.zlayer = []
        self.zlayer_kwargs = []
        self.kwargs['fig'] = None
        self.kwargs['ax'] = None
        if hard: self.kwargs = self._defaults.copy()

    def copy(self):
        new = self.__class__.__new__(self.__class__)
        new.__dict__ = self.__dict__.copy()
        new.reset()
        new.setup()
        return new

    def _update(self, *args, **kwargs):
        # args are new defined
        if args: 
            self.args = args
            self.newargs = True
        else:
            self.newargs = False
        
        # remove alias from kwargs 
        for k,v in kwargs.items():
            if k in util._alias:
                self.kwargs[util._alias[k]] = v
            self.kwargs.update({k:v})
        
        self._delete_unique_params()
        if plt.isinteractive(): self._redraw()

    def _setup_fig(self):
        fig = self.kwargs['fig']
        
        for kw in self.kwargs:
            if kw in util._figure_func:
                func = getattr(fig, util._figure_func[kw])
                func(self.kwargs[kw])
    
    def _setup_ax(self):
        ax = self.kwargs['ax']
        #TODO doesnt work?
        #ax.ticklabel_format(useOffset=False)
        
        for k,v in self.kwargs.items():
            if util._axes_func.get(k, False):
                func = getattr(ax, util._axes_func[k])
            elif k[0]=='x':
                func = getattr(ax.get_xaxis(), util._axes_special_case[k])
            elif k[0]=='y':
                func = getattr(ax.get_yaxis(), util._axes_special_case[k])
            elif k in self.kwarg_defaults:
                continue
            else:
                raise Exception('No such a method {}'.format(k))
            func(**v) if type(v) is dict else func(v)
                
    
    def _create_fig_and_axes(self):
        self.kwargs['fig'] = plt.figure(figsize=self.kwargs['figsize'],
                                        dpi=self.kwargs['dpi'])
        self.kwargs['ax'] = self.kwargs['fig'].gca()
        self.kwargs['fig'].add_axes(self.kwargs['ax'])
    
    def _create_fig_and_axes_subplots(self):
        self.kwargs['fig'],self.kwargs['ax'] = plt.subplots(
                figsize=self.kwargs['figsize'],
                dpi=self.kwargs['dpi'],
                sharex=self.kwargs.get('sharex',False),
                sharey=self.kwargs.get('sharey',False)
                )

         
    def _delete_unique_params(self):
        for kwarg in util._unique_params:
            self.kwargs.pop(kwarg, None)
    
    def _redraw(self):
        if plt.isinteractive():
            fig = self.kwargs['fig']
            if not plt.fignum_exists(fig.number):
                fig.show()
            fig.canvas.draw()
        else:
            print('Redraw() is unsupported in non-interactive plotting mode!')
    
    def _get_allowed_values(self, allowed, source=None):
        if not source: 
            source = self.kwargs
        if type(allowed) is dict:
            ret = {allowed[k]:v for k,v in source.items() if allowed.get(k,False)}
        elif type(allowed) is list:
            ret = {k:v for k,v in source.items() if k in allowed}
        else:
            ret = source
        return ret
    
    @staticmethod
    def save(path, form):
        plt.savefig(path, dataformat=form)
    
    @staticmethod
    def close():
        plt.close()
