#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under LGPLv3, see file LICENSE in this source tree.
"""
This module allows the creation of threads that will be used as repetitive
tasks for simulation purposes
"""
import time
import random
from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.io import curdoc, vplot
from bokeh.models.widgets import HBox, Slider, TextInput, VBoxForm


from bokeh.document import Document

from collections import OrderedDict
import logging
import math
import weakref

class BokehRenderer(object):

    def __init__(self, device, points_list, *, title = 'My title', daemon = True):
        self.device = device
        self.points_list = points_list
        self.title = title
        self.units = {}
        logging.getLogger("requests").setLevel(logging.INFO)
        logging.getLogger("bokeh").setLevel(logging.INFO)
#        self.app = Application()
        self.lst = self.points_list
        
        self.doc = Document()
        self.multi_states = self.device.multi_states
        self.binary_states = self.device.binary_states
        self.analog_units = self.device.analog_units 
        
        # Get data
    def read_lst(self):
        df = self.device[self.lst]
        try:
            df = df.fillna(method='ffill').fillna(method='bfill').replace(['inactive', 'active'], [0, 50])
        except TypeError:
            df = df.fillna(method='ffill').fillna(method='bfill')
                                      
        df = df.reset_index()
        df['name'] = 'nameToReplace'
        df['units'] = 'waiting for refresh'
        return df

    def read_notes(self):
        notes_df = self.device.notes.reset_index()
        notes_df['value'] = 100
        notes_df['desc'] = 'Notes'
        return notes_df

    def build_plot(self):        
        df = self.read_lst()
        notes_df = self.read_notes()

        TOOLS = "resize,hover,save,pan,box_zoom,wheel_zoom,reset"
        
        # Generate a figure container for notes
        self.p = Figure(plot_width=500, plot_height=450, x_axis_type="datetime", title = self.title, tools = TOOLS)

        self.notes_source = ColumnDataSource(
                    data=dict(
                        x = notes_df['index'],
                        y = notes_df['value'],
                        desc = notes_df['desc'],
                        units = notes_df[0]
                    )
                )
                

        self.p.asterisk('x', 
                        'y',
                        source = self.notes_source,
                        name = 'Notes',
                        color = "#%06x" % random.randint(0x000000, 0x777777), 
                        legend='Notes',
                        size = 40) 

        # plot = plot ?
        self.p = self.p
        self.p.legend.location = 'top_left'
        hover = self.p.select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ('name', '@desc'),
            ('value', '@y'),
            ('units', '@units'),
        ])
        
        # Build a plot for each point in list                
        for each in self.lst:
            try:
                df['name'] = df['name'].replace('nameToReplace', ('%s / %s' % (each, self.device[each]['description'])))            
            except TypeError:
                continue
            source = ColumnDataSource(
                            data=dict(
                            x = df['index'],
                            y = df[each],
                            desc = df['name'],
                            units = df['units']
                        )
                    )

            if each in self.binary_states:
                
                self.p.circle('x', 
                            'y',
                            source = source,
                            name = each,
                            color = "#%06x" % random.randint(0x000000, 0x777777), 
                            legend=each,
                            size = 10)
            elif each in self.multi_states:
                self.p.diamond('x', 
                            'y',
                            source = source,
                            name = each,
                            color = "#%06x" % random.randint(0x000000, 0x777777), 
                            legend=each,
                            size = 20)            
            else:
                self.p.line('x',
                            'y',
                            source = source,
                            name = each,
                            color = "#%06x" % random.randint(0x000000, 0x777777),
                            legend=each,
                            line_width = 2)
            
        layout = vplot(self.p)
        curdoc().add_root(layout)
        curdoc().add_periodic_callback(self.update_data, 1000)     
            
        

    def update_data(self):
        for renderer in self.p.renderers:
            name = renderer.name
            if name in self.lst:
                df = self.read_lst()                
                
                glyph_renderer = renderer
                df['name'] = df['name'].replace('nameToReplace', ('%s / %s' % (name, self.device[name]['description'])))
                glyph_renderer.data_source.data['x'] = df['index']
                glyph_renderer.data_source.data['y'] = df[name]
                glyph_renderer.data_source.data['desc'] = df['name']
                if name in self.multi_states:
                    glyph_renderer.data_source.data['units'] = [self.multi_states[name][int(math.fabs(x-1))] for x in df[name]]
                elif name in self.binary_states:
                    glyph_renderer.data_source.data['y'] = df[name]
                    glyph_renderer.data_source.data['units'] = [self.binary_states[name][int(x/50)] for x in df[name]]
                else:
                    df['units'] = self.analog_units[name]
                    glyph_renderer.data_source.data['units'] = df['units']
            elif name == 'Notes':
                notes_df = self.read_notes()
                glyph_renderer = renderer
                glyph_renderer.data_source.data['x'] = notes_df['index']
                glyph_renderer.data_source.data['y'] = notes_df['value']
                glyph_renderer.data_source.data['desc'] = notes_df['desc']
                glyph_renderer.data_source.data['units'] = notes_df[0]

    


    def choose_y_axis(self, point_name):
        """
        Could be use to select the y axis... not working yet...
        """
        if point_name in list(self.device.temperatures):
            return 'temperature'
        elif point_name in list(self.device.percent):
            return 'percent'
        else:
            return None

    def stop(self):
        self.exitFlag = True

    def beforeStop(self):
        """
        Action done when closing thread
        """
        pass
