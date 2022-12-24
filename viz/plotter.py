import sys
from PyQt5.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QAction, QStatusBar,
    QWidget, QVBoxLayout
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import numpy as np

class BasePlot(QMainWindow):
    def __init__(self):
        self._app = QApplication(sys.argv)
        super().__init__()
        
        # Initialize the plots and layout
        self.init_plots()
        self.init_layout()
        self.init_region()
        self.init_mouse()
        
    def init_plots(self):
        """Initialize the top and bottom plots. """
        self.top = pg.PlotWidget()
        self.bottom = pg.PlotWidget()
        
    def init_layout(self):
        """Initialize the layout and widget to hold the layout."""
        self.layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.top)
        self.layout.addWidget(self.bottom)
        self.setCentralWidget(self.widget)

    def init_region(self):
        """Initialize the linear region item and add it to the bottom plot."""
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        self.bottom.addItem(self.region, ignoreBounds=True)

        # Create bottom and left axes for the bottom plot
        bottom_axis = pg.graphicsItems.AxisItem.AxisItem(orientation='bottom', showValues=False)
        left_axis = pg.graphicsItems.AxisItem.AxisItem(orientation='left', showValues=False)
        self.bottom.getPlotItem().setAxisItems(axisItems={'bottom': bottom_axis, 'left': left_axis})
    
    def init_mouse(self):
        self._top_vLine = pg.InfiniteLine(angle=90, movable=False)
        self._top_hLine = pg.InfiniteLine(angle=0, movable=False)
        self.top.addItem(self._top_vLine, ignoreBounds=True)
        self.top.addItem(self._top_hLine, ignoreBounds=True)
        
    def connect_signals(self):
        """Connect the signals for updating the region and plots."""
        self.region.sigRegionChanged.connect(self.update_top_plot)
        self.top.sigRangeChanged.connect(self.update_region)
        proxy = pg.SignalProxy(self.top.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)
        self.top.scene().sigMouseMoved.connect(self.mouse_moved)
        self.top.scene().sigMouseClicked.connect(self.mouse_clicked)
        
    def update_top_plot(self):
        self.region.setZValue(10)
        min_x, max_x = self.region.getRegion()
        self.top.setXRange(min_x, max_x, padding=0)    

    def update_region(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)
        
    def mouse_moved(self, evt):
        pos = evt
        if self.top.sceneBoundingRect().contains(pos):
            mousePoint = self.top.plotItem.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            # if index > 0 and index < len(self._data[1,:]):
            #     label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
            self._top_vLine.setPos(mousePoint.x())
            self._top_hLine.setPos(mousePoint.y())
            
    def mouse_clicked(self, evt):
        """Handle mousle clicks"""
        pass
    
    def plot_data(self, **kwargs):
        """Plot the data on the top and bottom plots."""
        pass
    
    def set_tick_marks(self):
        """Set the tick marks for the left axis of the top plot."""
        pass
    
    def set_initial_region(self):
        """Set the initial region. """
        pass
    

class RawPlot(BasePlot):
    def __init__(self, info, data, times, picks=None):
        super().__init__()
        self.picks = picks
        self.info = info
        self._data = data
        self.times = times
        # Plot the data
        self.plot_data()
        
        # Set the initial region and connect the signals for updating the region and plots
        self.set_initial_region()
        self.connect_signals()

        # Set the tick marks for the left axis of the top plot
        self.set_tick_marks()
        
        self.show()
        self._app.exec()
    
    def plot_data(self, **kwargs):
        """Plot the data on the top and bottom plots."""
        
        for index, p in enumerate(self.picks):
            self.top.plot(self.times, self._data[:, p] + index/2)
            self.bottom.plot(self.times, self._data[:, p])
    
    def set_tick_marks(self):
        """Set the tick marks for the left axis of the top plot."""
        
        ticks = []
        ch_names = np.array(self.info['ch_names'])
        for index, chan in enumerate(ch_names[self.picks]):
            pos_y = self._data[:, index].min() + index/2
            label = chan
            ticks.append((pos_y, label))
        
        self.top.getPlotItem().getAxis('left').setTicks([
            ticks
            ])
    
    def set_initial_region(self):
        """Set the initial region to."""
        self.region.setRegion([0, self.times.max()])
        self.region.setBounds([0, self.times.max()])
        #self.region.setClipItem(self.bottom)


class EpochsPlot(BasePlot):
    def __init__(self, epochs, info, data, events, tmin, tmax, picks=None, event_id=None):
        super().__init__()
        self.picks = picks
        self.info = info
        self._data = data
        self.tmin = tmin
        self.tmax = tmax
        self.events = events
        self.n_times = self._data.shape[1] * self._data.shape[0]
        time = abs(tmin) + abs(tmax)
        self._last_time = self._data.shape[0] * time
        self.times = np.linspace(0, self._last_time, self.n_times)
        self.bad_epochs = np.full((1, self._data.shape[0]), False)[0]
        #print(self.bad_epochs)
        
        self._segments = self._get_segments()
        self._segment_boundings = self.init_segment_boxes()
        # Plot the data
        self.plot_data()
        
        # Set the initial region and connect the signals for updating the region and plots
        self.set_initial_region()
        self.connect_signals()

        # Set the tick marks for the left axis of the top plot
        self.set_tick_marks()
        
        self.show()
        self._app.exec()
        
        # This is bad, change later
        epochs.bad_epochs = self.bad_epochs
        
    def set_initial_region(self):
        """Set the initial region to."""
        self.region.setRegion([0, self.times.max()])
        self.region.setBounds([0, self.times.max()])
        
    def init_segment_boxes(self):
        """Initialize the bounding boxes of segments to track its state"""
        bounding_boxes = []
        
        for segment in self._segments:
            box = pg.LinearRegionItem(values=(segment[0], segment[1]), 
                                      movable=False, brush=pg.mkBrush(None),
                                      pen=pg.mkPen(None), bounds=(segment[0], segment[1]))
            box.setZValue(10)
            self.top.addItem(box, ignoreBounds=True)
            bounding_boxes.append(box)
        
        return bounding_boxes
    
        

        
    def plot_data(self, **kwargs):
        """Plot the data on the top and bottom plots."""
               
        data = self._data.reshape((self._data.shape[0] * self._data.shape[1], 
                           self._data.shape[2]))
        
        # Plot data
        for idx, p in enumerate(self.picks):
            self.top.plot(self.times, data[:, p] + idx/2)
            self.bottom.plot(self.times, data[:, p])
        
        # Plot seperators
        for i, segment in enumerate(self._segments):
            label = str(self.events[i, 1])
            v_bar = pg.InfiniteLine(pos=segment[1], angle=90, label=label, 
                                    labelOpts={'rotateAxis':(1,0), 'anchors':[(1,0.8),(1,0.8)], 'color':'r'})
            self.top.addItem(v_bar)

        """Set the tick marks for the y-axis and x-axis of the top plot """
        
        y_ticks = []
        ch_names = np.array(self.info['ch_names'])
        for index, chan in enumerate(ch_names[self.picks]):
            pos_y = self._data[:, index].min() + index/2
            label = chan
            y_ticks.append((pos_y, label))
        
        x_ticks = []
        x_tick_pos = self._get_x_tick_pos()
        
        for i, pos in enumerate(x_tick_pos):
            pos_x = pos
            label = str(i)
            x_ticks.append((pos_x, label))
        
        
        self.top.getPlotItem().getAxis('left').setTicks([
            y_ticks
            ])
        
        self.top.getPlotItem().getAxis('bottom').setTicks([
            x_ticks
            ])
        
    def mouse_clicked(self, evt):
        """Handle mouse clicks"""
        scene_coords = evt.scenePos()
        if self.top.sceneBoundingRect().contains(scene_coords):
            mouse_point = self.top.plotItem.vb.mapSceneToView(scene_coords)
            self._clicked_on_segment(mouse_point.x())
        
    def _get_segments(self):
        """Get start and end points of segments"""
        tuple_list = []
        
        dist = abs(self.tmin) + abs(self.tmax)
        #last_time = int(self._last_time * 1000)
        
        for i in np.arange(0, self._last_time, dist):
            tuple_list.append((i, i + dist))
        
        segments = np.array(tuple_list)
        
        return segments

    def _get_x_tick_pos(self):
        """Get positions for tick marks on the x-axis"""
        
        pos = []
        for tup in self._segments:
            value = (tup[0] + tup[1]) // 2
            pos.append(value)
            
        return pos
    
    def _clicked_on_segment(self, x):
        
        for index, segment in enumerate(self._segments):
            if self._in_range(x, segment):
                #print(f"Value {x} is in segment {segment} at index {index}")
                self._update_segment_box(index)
                self.bad_epochs[index] = not self.bad_epochs[index]
                
    def _update_segment_box(self, index):
        
        if not self.bad_epochs[index]:
            self._segment_boundings[index].setBrush((0, 0, 255, 50))
        else:
            self._segment_boundings[index].setBrush(None)
        
    def _in_range(self, val, t):
        return t[0] <= val <= t[1]

