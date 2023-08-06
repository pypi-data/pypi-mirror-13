# encoding: utf-8

'''
@author:     Jose Emilio Romero Lopez

@copyright:  Copyright 2013-2014, Jose Emilio Romero Lopez.

@license:    GPL

@contact:    jemromerol@gmail.com

  This file is part of APASVO.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from PySide import QtGui, QtCore
import matplotlib
import numpy as np
import traceback

matplotlib.rcParams['backend'] = 'qt4agg'
matplotlib.rcParams['backend.qt4'] = 'PySide'
matplotlib.rcParams['patch.antialiased'] = False
matplotlib.rcParams['agg.path.chunksize'] = 80000

from apasvo._version import __version__
from apasvo._version import _application_name
from apasvo._version import _organization
from apasvo.gui.views.generated import ui_tracewindow
from apasvo.gui.views.generated import qrc_icons
from apasvo.gui.delegates import cbdelegate
from apasvo.gui.models import eventlistmodel
from apasvo.gui.models import pickingtask
from apasvo.gui.views import svwidget
from apasvo.gui.views import navigationtoolbar
from apasvo.gui.views import takanamidialog
from apasvo.gui.views import staltadialog
from apasvo.gui.views import ampadialog
from apasvo.gui.views import playertoolbar
from apasvo.gui.views import error
from apasvo.picking import stalta
from apasvo.picking import ampa


class TraceWindow(QtGui.QMainWindow, ui_tracewindow.Ui_TraceWindow):
    """Application Trace Window class. SDI GUI style.

    Attributes:
        record: Current opened seismic document.
        isModified: Indicates whether there are any changes in results to save
            or not.
        saved_filename: Name of the file where results are being saved.
    """

    def __init__(self, trace, parent=None):
        super(TraceWindow, self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.isModified = False
        self.saved_filename = None
        self.saved_event_format = None
        self.saved_cf_filename = None
        self.saved_cf_format = None
        self.saved_cf_dtype = None
        self.saved_cf_byteorder = None

        # Create context menu for events table
        self.event_context_menu = QtGui.QMenu(self)
        self.event_context_menu.addAction(self.actionDelete_Selected)
        self.EventsTableView.customContextMenuRequested.connect(lambda: self.event_context_menu.exec_(QtGui.QCursor.pos()))
        self.EventsTableView.clicked.connect(self.goto_event_position)

        self.actionOpen.triggered.connect(self.open)
        self.actionSaveEvents.triggered.connect(self.save_events)
        self.actionSaveEvents_As.triggered.connect(self.save_events_as)
        self.actionSaveCF.triggered.connect(self.save_cf)
        self.actionSaveCF_As.triggered.connect(self.save_cf_as)
        self.actionClose.triggered.connect(self.close)
        self.actionQuit.triggered.connect(QtGui.qApp.closeAllWindows)
        self.actionClearRecent.triggered.connect(self.clear_recent_list)
        self.actionSettings.triggered.connect(self.edit_settings)
        self.actionSTA_LTA.triggered.connect(self.doSTALTA)
        self.actionAMPA.triggered.connect(self.doAMPA)
        self.actionTakanami.triggered.connect(self.doTakanami)
        self.actionClear_Event_List.triggered.connect(self.clear_events)
        self.actionDelete_Selected.triggered.connect(self.delete_selected_events)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionOnlineHelp.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(APASVO_URL)))
        # add navigation toolbar
        self.signalViewer = svwidget.SignalViewerWidget(self.splitter)
        self.splitter.addWidget(self.signalViewer)
        self.toolBarNavigation = navigationtoolbar.NavigationToolBar(self.signalViewer.canvas, self)
        self.toolBarNavigation.setEnabled(False)
        self.toolBarNavigation.view_restored.connect(self.signalViewer.subplots_adjust)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBarNavigation)
        self.addToolBarBreak()
        # add analysis toolbar
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBarAnalysis)
        self.addToolBarBreak()
        # add media toolbar
        settings = QtCore.QSettings(_organization, _application_name)
        settings.beginGroup('player_settings')
        fs = int(settings.value('playback_freq', playertoolbar.DEFAULT_REAL_FREQ))
        bd = settings.value('bit_depth', playertoolbar.DEFAULT_BIT_DEPTH)
        settings.endGroup()
        self.toolBarMedia = playertoolbar.PlayerToolBar(self, sample_freq=fs, bd=bd)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBarMedia)
        self.toolBarMedia.intervalChanged.connect(self.signalViewer.set_selector_limits)
        self.toolBarMedia.intervalSelected.connect(self.signalViewer.selector.set_active)
        self.toolBarMedia.tick.connect(self.signalViewer.set_playback_position)
        self.toolBarMedia.playingStateChanged.connect(lambda x: self.signalViewer.set_selection_enabled(not x))
        self.toolBarMedia.playingStateSelected.connect(lambda: self.signalViewer.set_playback_marker_visible(True))
        self.toolBarMedia.stoppedStateSelected.connect(lambda: self.signalViewer.set_playback_marker_visible(False))
        self.signalViewer.selector.toggled.connect(self.toolBarMedia.toggle_interval_selected)
        self.signalViewer.selector.valueChanged.connect(self.toolBarMedia.set_limits)
        self.addToolBarBreak()

        self.actionEvent_List.toggled.connect(self.EventsTableView.setVisible)

        self.actionSignal_Amplitude.toggled.connect(self.signalViewer.set_signal_amplitude_visible)
        self.actionSignal_Envelope.toggled.connect(self.signalViewer.set_signal_envelope_visible)
        self.actionEspectrogram.toggled.connect(self.signalViewer.set_espectrogram_visible)
        self.actionCharacteristic_Function.toggled.connect(self.signalViewer.set_cf_visible)
        self.actionSignal_MiniMap.toggled.connect(self.signalViewer.set_minimap_visible)
        self.signalViewer.selector.toggled.connect(self.on_selection_toggled)
        self.signalViewer.selector.valueChanged.connect(self.on_selection_changed)
        self.signalViewer.CF_loaded.connect(self.actionCharacteristic_Function.setEnabled)
        self.signalViewer.CF_loaded.connect(self.actionCharacteristic_Function.setChecked)
        self.signalViewer.event_selected.connect(self.on_event_picked)
        self.actionActivateThreshold.toggled.connect(self.toggle_threshold)

        self.actionTrace_Toolbar.toggled.connect(self.toolBarTrace.setVisible)
        self.actionMedia_Toolbar.toggled.connect(self.toolBarMedia.setVisible)
        self.actionAnalysis_Toolbar.toggled.connect(self.toolBarAnalysis.setVisible)
        self.actionNavigation_Toolbar.toggled.connect(self.toolBarNavigation.setVisible)

        self.set_title()
        self.set_recent_menu()

        self._load_trace(trace)

    def _load_trace(self, trace):
        # Create
        self.document = eventlistmodel.EventListModel(trace, self.command_stack)
        self.document.emptyList.connect(self.set_modified)
        self.actionUndo = self.document.command_stack.createUndoAction(self)
        self.actionRedo = self.document.command_stack.createRedoAction(self)
        self.EventsTableView.setModel(self.document)
        model = self.EventsTableView.selectionModel()
        model.selectionChanged.connect(self.on_event_selection)
        # Connect Delegates
        for i, attribute in enumerate(self.document.attributes):
            if attribute.get('attribute_type') == 'enum' and attribute.get('editable', False):
                delegate = cbdelegate.ComboBoxDelegate(self.EventsTableView,
                                                       attribute.get('value_list', []))
                self.EventsTableView.setItemDelegateForColumn(i, delegate)
            else:
                self.EventsTableView.setItemDelegateForColumn(i, None)
        # connect document model to signalViewer
        self.document.eventCreated.connect(self.signalViewer.create_event)
        self.document.eventDeleted.connect(self.signalViewer.delete_event)
        self.document.eventModified.connect(self.signalViewer.update_event)
        self.document.detectionPerformed.connect(self.signalViewer.update_cf)
        self.document.detectionPerformed.connect(self.toolBarNavigation.update)
        # load document data into signal viewer
        self.signalViewer.set_record(self.document)
        self.signalViewer.thresholdMarker.thresholdChanged.connect(self.thresholdSpinBox.setValue)
        self.signalViewer.set_signal_amplitude_visible(self.actionSignal_Amplitude.isChecked())
        self.signalViewer.set_signal_envelope_visible(self.actionSignal_Envelope.isChecked())
        self.signalViewer.set_cf_visible(self.actionCharacteristic_Function.isChecked())
        self.signalViewer.set_espectrogram_visible(self.actionEspectrogram.isChecked())
        self.signalViewer.set_minimap_visible(self.actionSignal_MiniMap.isChecked())
        self.signalViewer.set_threshold_visible(self.actionActivateThreshold.isChecked())
        self.signalViewer.thresholdMarker.set_threshold(self.thresholdSpinBox.value())
        self.thresholdSpinBox.valueChanged.connect(self.signalViewer.thresholdMarker.set_threshold)
        self.toolBarMedia.load_data(self.document.record.signal, self.document.record.fs)
        self.toolBarMedia.connect_path()
        # Update GUI
        self.centralwidget.setVisible(True)
        self.actionClose.setEnabled(True)
        self.actionClear_Event_List.setEnabled(True)
        self.actionSTA_LTA.setEnabled(True)
        self.actionAMPA.setEnabled(True)
        self.toolBarNavigation.setEnabled(True)
        self.toolBarAnalysis.setEnabled(True)
        self.toolBarMedia.set_enabled(True)
        self.set_title()

    def close(self):
        """Closes current document.

        If there are any changes to save, shows a dialog asking
        the user whether to save data or not.
        """
        if self.maybeSave():
            if self.document is not None:
                self.document.emptyList.disconnect(self.set_modified)
                self.document = None
            self.command_stack.clear()
            self.set_modified(False)
            self.saved_filename = None
            self.saved_event_format = None
            self.signalViewer.unset_record()
            self.toolBarMedia.disconnect_path()
            # Update GUI
            self.centralwidget.setVisible(False)
            self.actionClose.setEnabled(False)
            self.actionClear_Event_List.setEnabled(False)
            self.actionSTA_LTA.setEnabled(False)
            self.actionAMPA.setEnabled(False)
            self.toolBarNavigation.setEnabled(False)
            self.toolBarAnalysis.setEnabled(False)
            self.set_title()

    def closeEvent(self, event):
        """Current window's close event"""
        if self.maybeSave():
            # prevent toolBarMedia firing signals if it's on playing or paused state
            self.toolBarMedia.blockSignals(True)
            self.toolBarMedia.disconnect_path()
            event.accept()
        else:
            event.ignore()

    def set_modified(self, value):
        """Sets 'isModified' attribute's value"""
        self.isModified = value
        self.actionSaveEvents.setEnabled(value)
        self.actionSaveEvents_As.setEnabled(value)
        # If already computed, enable save CF
        cf_computed = False if self.document is None else len(self.document.record.cf) != 0
        self.actionSaveCF.setEnabled(cf_computed)
        self.actionSaveCF_As.setEnabled(cf_computed)

    def set_title(self):
        """Sets current window's title."""
        prefix = '' if self.document is None else "%s - " % str(self.document.record)
        self.setWindowTitle('%s%s v.%s' % (prefix, _application_name, __version__))

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()

    def toggle_threshold(self, value):
        """Set threshold checkbox's value"""
        self.thresholdLabel.setEnabled(value)
        self.thresholdSpinBox.setEnabled(value)
        self.signalViewer.thresholdMarker.set_visible(value)

    def doSTALTA(self):
        """Performs event detection/picking by using STA-LTA method."""
        dialog = staltadialog.StaLtaDialog(self.document)
        return_code = dialog.exec_()
        if return_code == QtGui.QDialog.Accepted:
            # Read settings
            settings = QtCore.QSettings(_organization, _application_name)
            settings.beginGroup('stalta_settings')
            sta_length = float(settings.value('sta_window_len', 5.0))
            lta_length = float(settings.value('lta_window_len', 100.0))
            settings.endGroup()
            # Get threshold value
            if self.actionActivateThreshold.isChecked():
                threshold = self.thresholdSpinBox.value()
            else:
                threshold = None
            # Create an STA-LTA algorithm instance with selected settings
            alg = stalta.StaLta(sta_length, lta_length)
            # perform task
            self._analysis_task = pickingtask.PickingTask(self.document, alg,
                                                                threshold)
            self.launch_analysis_task(self._analysis_task,
                                      label="Applying %s..." % alg.__class__.__name__.upper())

    def doAMPA(self):
        """Performs event detection/picking by using AMPA method."""
        dialog = ampadialog.AmpaDialog(self.document)
        return_code = dialog.exec_()
        if return_code == QtGui.QDialog.Accepted:
            # Read settings
            settings = QtCore.QSettings(_organization, _application_name)
            settings.beginGroup('ampa_settings')
            wlen = float(settings.value('window_len', 100.0))
            wstep = float(settings.value('step', 50.0))
            nthres = float(settings.value('noise_threshold', 90))
            filters = settings.value('filters', [30.0, 20.0, 10.0,
                                                               5.0, 2.5])
            filters = list(filters) if isinstance(filters, list) else [filters]
            filters = np.array(filters).astype(float)
            settings.beginGroup('filter_bank_settings')
            startf = float(settings.value('startf', 2.0))
            endf = float(settings.value('endf', 12.0))
            bandwidth = float(settings.value('bandwidth', 3.0))
            overlap = float(settings.value('overlap', 1.0))
            settings.endGroup()
            settings.endGroup()
            # Get threshold value
            if self.actionActivateThreshold.isChecked():
                threshold = self.thresholdSpinBox.value()
            else:
                threshold = None
            # Create an AMPA algorithm instance with selected settings
            alg = ampa.Ampa(wlen, wstep, filters, noise_thr=nthres,
                            bandwidth=bandwidth, overlap=overlap,
                            f_start=startf, f_end=endf)
            # perform task
            self._analysis_task = pickingtask.PickingTask(self.document, alg,
                                                                threshold)
            self.launch_analysis_task(self._analysis_task,
                                      label="Applying %s..." % alg.__class__.__name__.upper())

    def launch_analysis_task(self, task, label=""):
        self.actionAMPA.setEnabled(False)
        self.actionSTA_LTA.setEnabled(False)
        self.analysis_progress_bar.show()
        self.analysis_label.setText(label)
        self._thread = QtCore.QThread(self)
        task.moveToThread(self._thread)
        self._thread.started.connect(task.run)
        task.finished.connect(self._thread.quit)
        task.finished.connect(self.on_analysis_finished)
        task.finished.connect(task.deleteLater)
        task.error.connect(error.display_error_dlg)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def on_analysis_finished(self):
        self.actionAMPA.setEnabled(True)
        self.actionSTA_LTA.setEnabled(True)
        self.analysis_progress_bar.hide()
        self.analysis_label.setText("")

    def doTakanami(self):
        xleft, xright = self.signalViewer.get_selector_limits()
        takanamidialog.TakanamiDialog(self.document, xleft, xright).exec_()

    def clear_events(self):
        if self.document is not None:
            self.document.clearEvents()

    def delete_selected_events(self):
        if self.document is not None:
            selected_rows = self.EventsTableView.selectionModel().selectedRows()
            self.document.removeRows([row.row() for row in selected_rows])

    def goto_event_position(self, index):
        self.signalViewer.goto_event(self.document.record.events[index.row()])

    def on_event_selection(self, s, d):
        selected_events = [self.document.getEventByRow(index.row())
                           for index in self.EventsTableView.selectionModel().selectedRows()]
        self.actionDelete_Selected.setEnabled(len(selected_events) > 0)
        self.signalViewer.set_event_selection(selected_events)

    def on_event_picked(self, event):
        if self.document is not None:
            self.EventsTableView.selectionModel().clear()
            self.EventsTableView.selectionModel().select(self.document.index(self.document.indexOf(event), 0),
                                                         QtGui.QItemSelectionModel.ClearAndSelect |
                                                         QtGui.QItemSelectionModel.Rows)

    def on_selection_toggled(self, value):
        self.on_selection_changed(*self.signalViewer.get_selector_limits())

    def on_selection_changed(self, xleft, xright):
        selection_length = abs(xleft - xright)
        enable_takanami = (self.signalViewer.selector.active and
                           (selection_length >= (takanamidialog.MINIMUM_MARGIN_IN_SECS * 2)))
        self.actionTakanami.setEnabled(enable_takanami)
