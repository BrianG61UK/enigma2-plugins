# -*- coding: utf-8 -*-

from . import _
from RecordTimer import RecordTimerEntry, RecordTimer
from Screens.TimerEntry import TimerEntry
from Components.config import config, ConfigSelection, ConfigText, ConfigSubList, ConfigDateTime, ConfigClock, ConfigYesNo, getConfigListEntry
from Tools import Directories
from Tools.XMLTools import stringToXML
from Tools import Notifications
from Screens.MessageBox import MessageBox
import xml.etree.cElementTree
from Vps_setup import VPS_show_info
from Vps_check import VPS_check_PDC

vps_already_registered = False



def new_RecordTimer_saveTimer(self):
	self._saveTimer_old_rn_vps()
	
	# added by VPS-Plugin
	list = []
	list.append('<?xml version="1.0" ?>\n')
	list.append('<vps_timers>\n')
	
	try:	
		for timer in self.timer_list:
			if timer.dontSave or timer.vpsplugin_enabled is None or timer.vpsplugin_enabled == False:
				continue
			
			list.append('<timer')
			list.append(' begin="' + str(int(timer.begin)) + '"')
			list.append(' end="' + str(int(timer.end)) + '"')
			list.append(' serviceref="' + stringToXML(str(timer.service_ref)) + '"')
			list.append(' vps_enabled="1"')
			
			if timer.vpsplugin_overwrite is not None:
				list.append(' vps_overwrite="' + str(int(timer.vpsplugin_overwrite)) + '"')
			else:
				list.append(' vps_overwrite="0"')
			
			if timer.vpsplugin_time is not None:
				list.append(' vps_time="' + str(timer.vpsplugin_time) + '"')
			else:
				list.append(' vps_time="0"')
			
			list.append('>\n')
			list.append('</timer>\n')
		
		list.append('</vps_timers>\n')
		
		file = open(Directories.resolveFilename(Directories.SCOPE_CONFIG, "timers_vps.xml"), "w")
		for x in list:
			file.write(x)
		file.close()
	except:
	 pass
	# added by VPS-Plugin


def new_RecordTimer_loadTimer(self):
	# added by VPS-Plugin
	xmlroot = None
	try:
		global xml
		doc = xml.etree.cElementTree.parse(Directories.resolveFilename(Directories.SCOPE_CONFIG, "timers_vps.xml"))
		xmlroot = doc.getroot()
	except:
		pass
	# added by VPS-Plugin
	
	self._loadTimer_old_rn_vps()
	
	# added by VPS-Plugin
	try:
		vps_timers = { }
		
		if xmlroot is not None:
			for xml in xmlroot.findall("timer"):
				begin = xml.get("begin")
				end = xml.get("end")
				serviceref = xml.get("serviceref").encode("utf-8")
				
				vps_timers[serviceref + begin + end] = { }
				vps_overwrite = xml.get("vps_overwrite")
				if vps_overwrite and vps_overwrite == "1":
					vps_timers[serviceref + begin + end]["overwrite"] = True
				else:
					vps_timers[serviceref + begin + end]["overwrite"] = False
				
				vps_time = xml.get("vps_time")
				if vps_time and vps_time != "None":
					vps_timers[serviceref + begin + end]["time"] = int(vps_time)
				else:
					vps_timers[serviceref + begin + end]["time"] = 0
			
			for timer in self.timer_list:
				begin = str(timer.begin)
				end = str(timer.end)
				serviceref = str(timer.service_ref)
				
				if vps_timers.get(serviceref + begin + end, None) is not None:
					timer.vpsplugin_enabled = True
					timer.vpsplugin_overwrite = vps_timers[serviceref + begin + end]["overwrite"]
					if vps_timers[serviceref + begin + end]["time"] != 0:
						timer.vpsplugin_time = vps_timers[serviceref + begin + end]["time"]
				else:
					timer.vpsplugin_enabled = False
					timer.vpsplugin_overwrite = False
	except:
		pass
	# added by VPS-Plugin

def new_TimerEntry_createConfig(self):
	self._createConfig_old_rn_vps()
	
	# added by VPS-Plugin
	try:
		if self.timer.vpsplugin_enabled is not None:
			self.timerentry_vpsplugin_enabled = ConfigYesNo(default = self.timer.vpsplugin_enabled)
		elif self.timer.eit is not None and self.timer.name != "" and self.timer not in self.session.nav.RecordTimer.timer_list and self.timer not in self.session.nav.RecordTimer.processed_timers:
			self.timerentry_vpsplugin_enabled = ConfigYesNo(default = config.plugins.vps.default_vps.value)
		else:
			self.timerentry_vpsplugin_enabled = ConfigYesNo(default = False)

		if self.timer.vpsplugin_overwrite is not None:
			self.timerentry_vpsplugin_overwrite = ConfigYesNo(default = self.timer.vpsplugin_overwrite)
		elif config.plugins.vps.allow_overwrite.value == True:
			self.timerentry_vpsplugin_overwrite = ConfigYesNo(default = config.plugins.vps.default_overwrite.value)
		else:
			self.timerentry_vpsplugin_overwrite = ConfigYesNo(default = False)

		if self.timer.vpsplugin_time is not None:
			self.timerentry_vpsplugin_time_date = ConfigDateTime(default = self.timer.vpsplugin_time, formatstring = _("%d.%B %Y"), increment = 86400)
			self.timerentry_vpsplugin_time_clock = ConfigClock(default = self.timer.vpsplugin_time)
		else:
			self.timerentry_vpsplugin_time_date = ConfigDateTime(default = self.timer.begin, formatstring = _("%d.%B %Y"), increment = 86400)
			self.timerentry_vpsplugin_time_clock = ConfigClock(default = self.timer.begin)
	except:
		pass
	# added by VPS-Plugin


def new_TimerEntry_createSetup(self, widget):
	self._createSetup_old_rn_vps(widget)
	
	# added by VPS-Plugin
	self.timerVps_enabled_Entry = None
	try:
		if self.timerentry_justplay.value != "zap" and self.timerentry_type.value == "once" and config.plugins.vps.enabled.value == True:
			self.timerVps_enabled_Entry = getConfigListEntry(_("Enable VPS"), self.timerentry_vpsplugin_enabled)
			self.list.append(self.timerVps_enabled_Entry)
			if config.plugins.vps.allow_overwrite.value == True and self.timerentry_vpsplugin_enabled.value == True:
				self.list.append(getConfigListEntry(_("Recording controlled by channel"), self.timerentry_vpsplugin_overwrite))
			if self.timerentry_vpsplugin_enabled.value == True and (self.timer.eit is None or self.timer.name == ""):
				self.session.open(VPS_check_PDC, self.timerentry_service_ref, self)
				
				self.list.append(getConfigListEntry(_("VPS-Time (date)"), self.timerentry_vpsplugin_time_date))
				self.list.append(getConfigListEntry(_("VPS-Time (time)"), self.timerentry_vpsplugin_time_clock))
			
			# Hilfetext
			elif self.timerentry_vpsplugin_enabled.value == True and config.plugins.vps.infotext.value != 2:
				config.plugins.vps.infotext.value = 2
				config.plugins.vps.infotext.save()
				VPS_show_info(self.session)
	except:
		pass
	# added by VPS-Plugin
	self[widget].list = self.list
	self[widget].l.setList(self.list)
	

def new_TimerEntry_newConfig(self):
	self._newConfig_old_rn_vps()
	
	# added by VPS-Plugin
	if self["config"].getCurrent() == self.timerVps_enabled_Entry:
		self.createSetup("config")
		self["config"].setCurrentIndex(self["config"].getCurrentIndex() + 1)
	# added by VPS-Plugin


def new_TimerEntry_keyGo(self):
	# added by VPS-Plugin
	try:
		self.timer.vpsplugin_enabled = self.timerentry_vpsplugin_enabled.value
		self.timer.vpsplugin_overwrite = self.timerentry_vpsplugin_overwrite.value
		if self.timer.vpsplugin_enabled == True and self.timer.name == "":
			self.timer.vpsplugin_time = self.getTimestamp(self.timerentry_vpsplugin_time_date.value, self.timerentry_vpsplugin_time_clock.value)
		if self.timer.vpsplugin_enabled == True:
			from Plugins.SystemPlugins.vps.Vps import vps_timers
			vps_timers.checksoon()
	except:
		pass
	# added by VPS-Plugin
	
	self._keyGo_old_rn_vps()




# VPS-Plugin in Enigma-Klassen einhängen
def register_vps():
	global vps_already_registered
	
	if vps_already_registered == False:
		RecordTimerEntry.vpsplugin_enabled = None
		RecordTimerEntry.vpsplugin_overwrite = None
		RecordTimerEntry.vpsplugin_time = None
		
		RecordTimer._saveTimer_old_rn_vps = RecordTimer.saveTimer
		RecordTimer.saveTimer = new_RecordTimer_saveTimer
		
		RecordTimer._loadTimer_old_rn_vps = RecordTimer.loadTimer
		RecordTimer.loadTimer = new_RecordTimer_loadTimer
		
		
		TimerEntry._createConfig_old_rn_vps = TimerEntry.createConfig
		TimerEntry.createConfig = new_TimerEntry_createConfig
		
		TimerEntry._createSetup_old_rn_vps = TimerEntry.createSetup
		TimerEntry.createSetup = new_TimerEntry_createSetup
		
		TimerEntry._newConfig_old_rn_vps = TimerEntry.newConfig
		TimerEntry.newConfig = new_TimerEntry_newConfig
		
		TimerEntry._keyGo_old_rn_vps = TimerEntry.keyGo
		TimerEntry.keyGo = new_TimerEntry_keyGo
		
		vps_already_registered = True