from hyperspyui.plugins.plugin import Plugin
import numpy as np
from hyperspy.api import *
import os
import csv
from datetime import datetime
import locale

from python_qt_binding import QtGui, QtCore
from QtCore import *
from QtGui import *

from hyperspyui.plugins.fitting import RegressionTool
from hyperspy.roi import BaseInteractiveROI
from scipy import stats
from hyperspy.utils.markers import line_segment, text


class CustomRegressionTool(RegressionTool):
    def get_category(self):
        return "Custom"


class ExtractKinetics(Plugin):
    name = "Extract kinetics"

    def create_actions(self):
        self.add_action(self.name + '.find_interface', "Find interface",
                        self.find_interface,
                        icon="analysis.svg",
                        tip="Find a vertical interface.")
        self.add_action(self.name + '.write_csv', "Save data",
                        self.write_csv,
                        icon="save.svg",
                        tip="Save out data as CSV.")

    def create_menu(self):
        self.add_menuitem('Custom',
                          self.ui.actions[self.name + '.find_interface'])
        self.add_menuitem('Custom', self.ui.actions[self.name + '.write_csv'])

    def create_toolbars(self):
        self.add_toolbar_button('Custom',
                                self.ui.actions[self.name + '.find_interface'])
        self.add_toolbar_button('Custom',
                                self.ui.actions[self.name + '.write_csv'])

    def create_tools(self):
        self.reg_tool = CustomRegressionTool(name='Kinetics regression')
        self.reg_tool.accepted[BaseInteractiveROI].connect(self.regression)
        self.add_tool(self.reg_tool, self.ui.select_signal)

    def find_interface(self, signal=None):
        if signal is None:
            s = self.ui.get_selected_signal()
        else:
            s = signal
        if s is None:
            return
        self._signal = s
        axes = s.axes_manager.signal_axes
        s0 = axes[0].scale * axes[0].size
        s1 = axes[1].scale * axes[1].size
        self._roi = utils.roi.RectangularROI(
            axes[0].offset + s0/2 - s0/20,
            axes[1].offset + s1/2 - s1/20,
            axes[0].offset + s0/2 + s0/20,
            axes[1].offset + s1/2 + s1/20)
        self._roi.add_widget(s)

        mb = QMessageBox(QMessageBox.Question, "Waiting for input",
                         "Click OK when interface ROI has been positioned.",
                         QMessageBox.Ok | QMessageBox.Cancel, parent=self.ui)
        mb.setWindowModality(Qt.NonModal)
        mb.finished.connect(self._on_continue_find)
        mb.show()

    def _on_continue_find(self, result):
        if not result or result == QMessageBox.Cancel:
            self._roi.remove_widget(self._signal)
            return
        s = self._roi(self._signal).sum(axis='x')
        self._roi.remove_widget(self._signal)

        s.change_dtype(float)
        s.axes_manager.set_signal_dimension(1)
        ds = s.diff(axis=1)
        ds.smooth_savitzky_golay(kind="livemodal")
        m = create_model(ds)
        g = components.Gaussian()
        m.append(g)
        m.fit_component(g, kind='livemodal')
        m.spectrum._plot.close()
        m.multifit()
        # Make signal of data
        s_pos = g.centre.as_signal()
        s_pos = signals.Signal(
            s_pos.data,
            axes=[s_pos.axes_manager._axes[0].get_axis_dictionary()],
            metadata=s.metadata.as_dictionary(),
            original_metadata=s.original_metadata.as_dictionary())
        s_pos.axes_manager.set_signal_dimension(1)
        s_pos.plot()
        # TODO: Name intensity axes
        m = utils.plot.markers.horizontal_line(y=s_pos.data, color='blue')
        self._signal.add_marker(m)

    @staticmethod
    def _get_times(signal):
        times = None
        if 'ser_header_parameters' in signal.original_metadata:
            times = signal.original_metadata.ser_header_parameters.Time
        elif 'stack_elements' in signal.original_metadata:
            times = [
                el.original_metadata.ser_header_parameters.Time
                for _, el in sorted(
                    signal.original_metadata.stack_elements,
                    key=lambda pair: int(pair[0].lstrip("element")))]
        elif 'ImageList' in signal.original_metadata:
            # Data in DM file, made by plugin
            tags = signal.original_metadata.ImageList.TagGroup0.ImageTags
            root = tags.plane_info
            # Currently, 'added__tick' is bugged, so parse 'added_time'
            times = []
            start = None
            old_lc = locale.getlocale(locale.LC_TIME)
            locale.setlocale(locale.LC_TIME, "C")
            try:
                for i in xrange(len(root)):
                    rt = root['TagGroup%d' % i].added__time
                    st = datetime.strptime(rt, "%I:%M:%S %p")
                    if start is None:
                        start = datetime(st.year, st.month, st.day)
                    t = (st - start).total_seconds()
                    times.append(t)
            finally:
                locale.setlocale(locale.LC_TIME, old_lc)
        return times

    def regression(self, roi, signal=None, axes=None):
        if signal is None:
            # If no signal passed, get it from tool
            f = self.reg_tool.widget.ax.figure
            window = f.canvas.parent()
            sw = window.property('hyperspyUI.SignalWrapper')
            if sw is None:
                return
            signal = sw.signal

        sig_axes = signal.axes_manager._axes
        if axes is None:
            # If no axes passed, get from tool
            axes = self.reg_tool.axes
        else:
            axes = sig_axes[axes]

        # Slice axes according to ROI (use only selected region for regression)
        i_ax = sig_axes.index(axes[0])
        slices = roi._make_slices(sig_axes, axes)
        for i, a in enumerate(sig_axes):
            if i != i_ax:
                slices[i] = a.index

        # Get scatter data (time data could be scattered)
        y = signal.data[slices]
        times = self._get_times(signal)    # Raw time data
        x = times[slices[i_ax]]            # Time data in ROI
        px = axes[0].axis[slices[i_ax]]    # Ordered x-data (for plot)

        # TODO: If in signal dim, iterate through navigation space
        reg = stats.linregress(x, y)       # Real regression
        preg = stats.linregress(px, y)     # Regression in plot
        x1, x2 = np.min(px), np.max(px)
        y1, y2 = np.array([x1, x2]) * preg[0] + preg[1]
        m_l = line_segment(x1, y1, x2, y2)
        signal.add_marker(m_l)
        unit = r'm/s'
        m_t = text((x2+x1)*0.5, (y2+y1)*0.5,
                   r"y = %.4g %s, R=%.4g, $\sigma$=%.4g" % (reg[0], unit,
                                                            reg[2], reg[4]))
        signal.add_marker(m_t)
        print('Speed, R, sigma:', reg[0], reg[2], reg[4])

        self.record_code("signal = ui.get_selected_signal()")
        self.record_code("axes = " +
                         str(tuple([sig_axes.index(a) for a in axes])))
        self.record_code("roi = utils.roi." + str(roi))
        self.record_code("<p>.regression(roi, signal, axes)")
        self.reg_tool.cancel()   # Turn off functionality as we are finished

    def write_csv(self, signal=None):
        if signal is None:
            s = self.ui.get_selected_signal()
        else:
            s = signal

        filename = QFileDialog.getSaveFileName(
            self.ui, "Save data", os.path.dirname(self.ui.cur_dir),
            "*.csv;;All types (*.*)",
            "*.csv")[0]

        if filename:
            with open(filename, 'wb') as f:
                c = csv.DictWriter(f, ["Time", "Shift"], delimiter='\t')
                c.writeheader()
                times = self._get_times(s)
                n = min(len(times), s.axes_manager.signal_axes[0].size)
                for i in xrange(n):
                    c.writerow({'Time': times[i], 'Shift': s.data[i]})
