# -*- coding: utf-8 -*-
#
# AWL simulator
#
# Copyright 2012-2016 Michael Buesch <m@bues.ch>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from __future__ import division, absolute_import, print_function, unicode_literals
from awlsim.common.compat import *

from awlsim.common.project import *

from awlsim.core.util import *
from awlsim.core.parser import *
from awlsim.core.cpu import *
from awlsim.core.hardware import *


def AwlSim_decorator_profiled(profileLevel):
	"""Profiled call decorator.
	"""
	def profiled_decorator(func):
		@functools.wraps(func)
		def profiled_wrapper(self, *args, **kwargs):
			if self._profileLevel >= profileLevel:
				self._profileStart()
			try:
				func(self, *args, **kwargs)
			finally:
				if self._profileLevel >= profileLevel:
					self._profileStop()
		return profiled_wrapper
	return profiled_decorator

def AwlSim_decorator_throwsAwlSimError(func):
	"""Handler decorator for AwlSimError exceptions.
	"""
	@functools.wraps(func)
	def awlSimErrorExtension_wrapper(self, *args, **kwargs):
		try:
			func(self, *args, **kwargs)
		except AwlSimError as e:
			self._handleSimException(e)
	return awlSimErrorExtension_wrapper

class AwlSim(object):
	"""Main awlsim core object.
	"""

	profiled		= AwlSim_decorator_profiled
	throwsAwlSimError	= AwlSim_decorator_throwsAwlSimError

	def __init__(self, profileLevel=0):
		self.__registeredHardware = []
		self.cpu = S7CPU()
		self.cpu.setPeripheralReadCallback(self.__peripheralReadCallback)
		self.cpu.setPeripheralWriteCallback(self.__peripheralWriteCallback)

		self.__setProfiler(profileLevel)

	def getCPU(self):
		return self.cpu

	def __setProfiler(self, profileLevel):
		self._profileLevel = profileLevel
		if self._profileLevel <= 0:
			return

		try:
			import cProfile as profileModule
		except ImportError:
			profileModule = None
		self.__profileModule = profileModule
		try:
			import pstats as pstatsModule
		except ImportError:
			pstatsModule = None
		self.__pstatsModule = pstatsModule

		if not self.__profileModule or\
		   not self.__pstatsModule:
			raise AwlSimError("Failed to load cProfile/pstats modules. "
				"Cannot enable profiling.")

		self.__profiler = self.__profileModule.Profile()

	def _profileStart(self):
		self.__profiler.enable()

	def _profileStop(self):
		self.__profiler.disable()

	def getProfileStats(self):
		if self._profileLevel <= 0:
			return None

		sio = StringIO()
		ps = self.__pstatsModule.Stats(self.__profiler,
					       stream = sio)
		ps.sort_stats("cumulative")
		ps.print_stats()

		return sio.getvalue()

	def _handleSimException(self, e):
		if not e.getCpu():
			# The CPU reference is not set, yet.
			# Set it to the current CPU.
			e.setCpu(self.cpu)
		raise e

	@throwsAwlSimError
	def __handleMaintenanceRequest(self, e):
		if e.requestType in (MaintenanceRequest.TYPE_SHUTDOWN,
				     MaintenanceRequest.TYPE_STOP,
				     MaintenanceRequest.TYPE_RTTIMEOUT):
			# This is handled in the toplevel loop, so
			# re-raise the exception.
			raise e
		try:
			if e.requestType == MaintenanceRequest.TYPE_SOFTREBOOT:
				# Run the CPU startup sequence again
				self.cpu.startup()
			else:
				assert(0)
		except MaintenanceRequest as e:
			raise AwlSimError("Recursive maintenance request")

	@profiled(2)
	@throwsAwlSimError
	def reset(self):
		self.cpu.reset()
		self.unregisterAllHardware(inCpuReset = True)

	@profiled(2)
	@throwsAwlSimError
	def load(self, parseTree, rebuild = False, sourceManager = None):
		self.cpu.load(parseTree, rebuild, sourceManager)

	@profiled(2)
	@throwsAwlSimError
	def loadSymbolTable(self, symTab, rebuild = False):
		self.cpu.loadSymbolTable(symTab, rebuild)

	@profiled(2)
	@throwsAwlSimError
	def loadLibraryBlock(self, libSelection, rebuild = False):
		self.cpu.loadLibraryBlock(libSelection, rebuild)

	@profiled(2)
	@throwsAwlSimError
	def removeBlock(self, blockInfo, sanityChecks = True):
		self.cpu.removeBlock(blockInfo, sanityChecks)

	@profiled(2)
	@throwsAwlSimError
	def staticSanityChecks(self):
		self.cpu.staticSanityChecks()

	@profiled(2)
	@throwsAwlSimError
	def startup(self):
		for hw in self.__registeredHardware:
			hw.startup()
		try:
			self.cpu.startup()
		except MaintenanceRequest as e:
			self.__handleMaintenanceRequest(e)

	def runCycle(self):
		if self._profileLevel >= 1:
			self._profileStart()

		try:
			for hw in self.__registeredHardware:
				hw.readInputs()
			self.cpu.runCycle()
			for hw in self.__registeredHardware:
				hw.writeOutputs()
		except AwlSimError as e:
			self._handleSimException(e)
		except MaintenanceRequest as e:
			self.__handleMaintenanceRequest(e)

		if self._profileLevel >= 1:
			self._profileStop()

	def unregisterAllHardware(self, inCpuReset = False):
		newHwList = []
		for hw in self.__registeredHardware:
			if not hw.getParam("removeOnReset") and inCpuReset:
				# This module has "removeOnReset" set to False
				# and we are in a CPU reset.
				# Do shutdown the module, but keep it in the
				# list of registered modules.
				newHwList.append(hw)
			hw.shutdown()
		self.__registeredHardware = newHwList

	def registerHardware(self, hwClassInst):
		"""Register a new hardware interface."""

		self.__registeredHardware.append(hwClassInst)

	def registerHardwareClass(self, hwClass, parameters={}):
		"""Register a new hardware interface class.
		'parameters' is a dict of hardware specific parameters.
		Returns the instance of the hardware class."""

		hwClassInst = hwClass(sim = self,
				      parameters = parameters)
		self.registerHardware(hwClassInst)
		return hwClassInst

	@classmethod
	def loadHardwareModule(cls, name):
		"""Load a hardware interface module.
		'name' is the name of the module to load (without 'awlsimhw_' prefix).
		Returns the HardwareInterface class."""

		return HwModLoader.loadModule(name).getInterface()

	def __peripheralReadCallback(self, userData, width, offset):
		# The CPU issued a direct peripheral read access.
		# Poke all registered hardware modules, but only return the value
		# from the last module returning a valid value.

		retValue = None
		for hw in self.__registeredHardware:
			value = hw.directReadInput(width, offset)
			if value is not None:
				retValue = value
		return retValue

	def __peripheralWriteCallback(self, userData, width, offset, value):
		# The CPU issued a direct peripheral write access.
		# Send the write request down to all hardware modules.
		# Returns true, if any hardware accepted the value.

		retOk = False
		for hw in self.__registeredHardware:
			ok = hw.directWriteOutput(width, offset, value)
			if not retOk:
				retOk = ok
		return retOk

	def __repr__(self):
		return str(self.cpu)
