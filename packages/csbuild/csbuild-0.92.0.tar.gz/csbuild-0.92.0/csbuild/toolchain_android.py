# Copyright (C) 2013 Jaedyn K. Draper
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Contains a plugin class for creating android NDK projects
"""
import glob
import platform
import os
import shutil
import subprocess
import sys
import shlex
import re
import platform

from . import toolchain
from . import toolchain_gcc
from . import log
from . import _shared_globals
import csbuild

if platform.system() == "Windows":
	__CSL = None
	import ctypes
	def symlink(source, link_name):
		'''symlink(source, link_name)
		   Creates a symbolic link pointing to source named link_name'''
		global __CSL
		if __CSL is None:
			csl = ctypes.windll.kernel32.CreateSymbolicLinkW
			csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
			csl.restype = ctypes.c_ubyte
			__CSL = csl
		flags = 0
		if source is not None and os.path.isdir(source):
			flags = 1
		if __CSL(link_name, source, flags) == 0:
			raise ctypes.WinError()
else:
	symlink = os.symlink

class AndroidBase( object ):
	def __init__(self):
		#TODO: Figure out a way to share some of this data between compiler and linker
		self.shared._ndkHome = os.getenv("NDK_HOME")
		self.shared._sdkHome = os.getenv("ANDROID_HOME")
		self.shared._antHome = os.getenv("ANT_HOME")
		self.shared._javaHome = os.getenv("JAVA_HOME")
		#self.shared._maxSdkVersion = 19
		#TODO: Determine this from highest number in the filesystem.
		self.shared._targetSdkVersion = 19
		self.shared._minSdkVersion = 9
		self.shared._packageName = "csbuild.autopackage"
		self.shared._activityName = None
		self.shared._usedFeatures = []
		self.shared._usedPermissions = [ "INTERNET", "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE" ]
		self.shared._sysRootDir = ""
		self.shared._keystoreLocation = ""
		self.shared._keystorePwFile = ""
		self.shared._keyPwFile = ""
		self.shared._keystoreAlias = ""
		self.shared._stlVersion = "GNU"
		self.shared._addNativeAppGlue = True


	def _copyTo(self, other):
		other.shared._ndkHome = self.shared._ndkHome
		other.shared._sdkHome = self.shared._sdkHome
		other.shared._antHome = self.shared._antHome
		other.shared._javaHome = self.shared._javaHome
		#other.shared._maxSdkVersion = self.shared._maxSdkVersion
		other.shared._targetSdkVersion = self.shared._targetSdkVersion
		other.shared._minSdkVersion = self.shared._minSdkVersion
		other.shared._packageName = self.shared._packageName
		other.shared._activityName = self.shared._activityName
		other.shared._usedFeatures = list(self.shared._usedFeatures)
		other.shared._usedPermissions = list(self.shared._usedPermissions)
		other.shared._sysRootDir = self.shared._sysRootDir
		other.shared._keystoreLocation = self.shared._keystoreLocation
		other.shared._keystorePwFile = self.shared._keystorePwFile
		other.shared._keyPwFile = self.shared._keyPwFile
		other.shared._keystoreAlias = self.shared._keystoreAlias
		other.shared._stlVersion = self.shared._stlVersion
		other.shared._addNativeAppGlue = self.shared._addNativeAppGlue


	def SetNdkHome(self, pathToNdk):
		self.shared._ndkHome = os.path.abspath(pathToNdk)


	def SetSdkHome(self, pathToSdk):
		self.shared._sdkHome = os.path.abspath(pathToSdk)


	def SetAntHome(self, pathToAnt):
		self.shared._antHome = os.path.abspath(pathToAnt)


	def SetJavaHome(self, pathToJava):
		self.shared._javaHome = os.path.abspath(pathToJava)


	def SetKeystoreLocation(self, pathToKeystore):
		self.shared._keystoreLocation = os.path.abspath(pathToKeystore)
		if not self.shared._keystorePwFile:
			self.shared._keystorePwFile = os.path.join(csbuild.mainfileDir, os.path.basename(pathToKeystore+".pass"))


	def SetKeystorePasswordFile(self, pathToPwFile):
		self.shared._keystorePwFile = os.path.abspath(pathToPwFile)


	def SetKeyPasswordFile(self, pathToPwFile):
		self.shared._keyPwFile = os.path.abspath(pathToPwFile)


	def SetKeystoreAlias(self, alias):
		self.shared._keystoreAlias = alias


	def SetMinSdkVersion(self, version):
		self.shared._minSdkVersion = version


	#def SetMaxSdkVersion(self, version):
	#	self.shared._maxSdkVersion = version


	def SetTargetSdkVersion(self, version):
		self.shared._targetSdkVersion = version


	def SetPackageName(self, name):
		self.shared._packageName = name


	def SetActivityName(self, name):
		self.shared._activityName = name


	def AddUsedFeatures(self, *args):
		self.shared._usedFeatures += list(args)


	def AddUsedPermissions(self, *args):
		self.shared._usedPermissions += list(args)


	def SetNativeAppGlue(self, addGlue):
		self.shared._addNativeAppGlue = addGlue


	def GetValidArchitectures(self):
		return ['x86', 'armeabi', 'armeabi-v7a', 'armeabi-v7a-hard', 'mips']


	def IsAndroidDebugBuild( self, project ):
		return project.optLevel != csbuild.OptimizationLevel.Max


	def _getTargetTriple(self, project):
		if self.shared.isClang:
			if project.outputArchitecture == "x86":
				return "-target i686-linux-android"
			elif project.outputArchitecture == "mips":
				return "-target mipsel-linux-android"
			elif project.outputArchitecture == "armeabi":
				return "-target armv7-linux-androideabi"
			else:
				return "-target armv7a-linux-androideabi"
		else:
			return ""

	def _getSimplifiedArch(self, project):
		if project.outputArchitecture.startswith("arm"):
			return "arm"
		return project.outputArchitecture

	def _setSysRootDir(self, project):
		self.shared._sysRootDir = os.path.join(
			self.shared._ndkHome,
			"platforms",
			"android-{}".format(self.shared._targetSdkVersion),
			"arch-{}".format(self._getSimplifiedArch(project)),
		)
		return


	def _getCommands(self, project, cmd1, cmd2, searchInLlvmPath = False):
		toolchainsDir = os.path.join(self.shared._ndkHome, "toolchains")
		arch = self._getSimplifiedArch(project)

		dirs = glob.glob(os.path.join(toolchainsDir, "{}*".format("llvm" if searchInLlvmPath else arch)))

		bestCompilerVersion = ""

		for dirname in dirs:
			prebuilt = os.path.join(toolchainsDir, dirname, "prebuilt")
			if not os.access(prebuilt, os.F_OK):
				continue

			if dirname > bestCompilerVersion:
				bestCompilerVersion = dirname

		if not bestCompilerVersion:
			log.LOG_ERROR("Couldn't find compiler for architecture {}.".format(project.outputArchitecture))
			csbuild.Exit(1)

		if platform.system() == "Windows":
			platformName = "windows"
			ext = ".exe"
		else:
			platformName = "linux"
			ext = ""

		cmd1Name = cmd1 + ext
		cmd2Name = cmd2 + ext

		binDir = os.path.join(toolchainsDir, bestCompilerVersion, "prebuilt", platformName)
		dirs = list(glob.glob("{}*".format(binDir)))
		binDir = os.path.join(dirs[0], "bin")
		maybeCmd1 = os.path.join(binDir, cmd1Name)

		if os.access(maybeCmd1, os.F_OK):
			cmd1Result = maybeCmd1
			cmd2Result = os.path.join(binDir, cmd2Name)
		else:
			dirs = list(glob.glob(os.path.join(binDir, "*-{}".format(cmd1Name))))
			prefix = dirs[0].rsplit('-', 1)[0]
			cmd1Result = dirs[0]
			cmd2Result = "{}-{}".format(prefix, cmd2Name)

		return cmd1Result, cmd2Result


class AndroidCompiler(AndroidBase, toolchain_gcc.GccCompiler):
	def __init__(self, shared):
		toolchain_gcc.GccCompiler.__init__(self, shared)
		AndroidBase.__init__(self)

		self._toolchainPath = ""
		self._setupCompleted = False

	def copy(self, shared):
		ret = toolchain_gcc.GccCompiler.copy(self, shared)
		AndroidBase._copyTo(self, ret)
		ret._toolchainPath = self._toolchainPath
		ret._setupCompleted = self._setupCompleted
		return ret

	def postPrepareBuildStep(self, project):
		if project.metaType == csbuild.ProjectType.Application and self.shared._addNativeAppGlue:
			appGlueDir = os.path.join( self.shared._ndkHome, "sources", "android", "native_app_glue" )
			project.includeDirs.append(appGlueDir)
			project.extraDirs.append(appGlueDir)
			project.RediscoverFiles()

	def GetDefaultArchitecture(self):
		return "armeabi-v7a"

	def _setupCompiler(self, project):
		#TODO: Let user choose which compiler version to use; for now, using the highest numbered version.

		if self.shared.isClang:
			ccName = "clang"
			cxxName = "clang++"
		else:
			ccName = "gcc"
			cxxName = "g++"

		self._settingsOverrides["cc"], self._settingsOverrides["cxx"] = self._getCommands(project, ccName, cxxName, self.shared.isClang)

	def _setupForProject( self, project ):
		#toolchain_gcc.compiler_gcc.SetupForProject(self, project)
		if not self._setupCompleted:
			if "clang" in project.cc or "clang" in project.cxx:
				self.shared.isClang = True
			self._setupCompiler(project)
			self._setSysRootDir(project)
			self._setupCompleted = True

	def prePrepareBuildStep(self, project):
		self._setupForProject(project)
		#Applications on Android have to build as shared libraries
		project.metaType = project.type
		if project.type == csbuild.ProjectType.Application:
			project.type = csbuild.ProjectType.SharedLibrary
			if not project.outputName.startswith("lib"):
				project.outputName = "lib{}".format(project.outputName)
		elif project.type == csbuild.ProjectType.SharedLibrary:
			project.type = csbuild.ProjectType.StaticLibrary

	def _getSystemDirectories(self, project, isCpp):
		ret = ""
		if isCpp:
			if self.shared._stlVersion == "GNU":
				ret += "-isystem \"{}\" ".format(os.path.join(
					self.shared._ndkHome,
					"sources",
					"cxx-stl",
					"gnu-libstdc++",
					"4.8",
					"libs",
					project.outputArchitecture,
					"include")
				)
				ret += "-isystem \"{}\" ".format(os.path.join( self.shared._ndkHome, "sources", "cxx-stl", "gnu-libstdc++", "4.8", "include"))
			elif self.shared._stlVersion == "stlport":
				ret += "-isystem \"{}\" ".format(os.path.join( self.shared._ndkHome, "sources", "cxx-stl", "system", "include"))
				ret += "-isystem \"{}\" ".format(os.path.join( self.shared._ndkHome, "sources", "cxx-stl", "stlport", "stlport"))
			elif self.shared._stlVersion == "libc++":
				ret += "-isystem \"{}\" ".format(os.path.join( self.shared._ndkHome, "sources", "cxx-stl", "llvm-libc++", "libcxx", "include"))


		ret += "--sysroot \"{}\" ".format(self.shared._sysRootDir)
		ret += "-isystem \"{}\" ".format(
			os.path.join(
				self.shared._ndkHome,
				"platforms",
				"android-{}".format(self.shared._targetSdkVersion),
				"arch-{}".format(self._getSimplifiedArch(project)),
				"usr",
				"include"
			)
		)

		ret += '-I "{}" '.format(self.shared._ndkHome)
		return ret

	def _getBaseCommand( self, compiler, project, isCpp ):
		self._setupForProject(project)

		if not self.shared.isClang:
			exitcodes = "-pass-exit-codes"
		else:
			exitcodes = ""

		if isCpp:
			if self._settingsOverrides["cxx"]:
				compiler = self._settingsOverrides["cxx"]
			standard = self.cppStandard
		else:
			if self._settingsOverrides["cc"]:
				compiler = self._settingsOverrides["cc"]
			standard = self.cStandard

		if project.type == csbuild.ProjectType.SharedLibrary or project.type == csbuild.ProjectType.LoadableModule:
			picFlag = "-fPIC "
		else:
			picFlag = ""

		cmds = "\"{}\" {} -Winvalid-pch -c {}-g{} -O{} {}{}{} {} {} {}".format(
			compiler,
			exitcodes,
			self._getDefines( project.defines, project.undefines ),
			project.debugLevel,
			project.optLevel,
			picFlag,
			"-pg " if project.profile else "",
			"--std={0}".format( standard ) if standard != "" else "",
			" ".join( project.cxxCompilerFlags ) if isCpp else " ".join( project.ccCompilerFlags ),
			self._getSystemDirectories(project, isCpp),
			self._getTargetTriple(project)
		)

		return cmds.replace("\\", "/")

	def _getIncludeDirs( self, includeDirs ):
		"""Returns a string containing all of the passed include directories, formatted to be passed to gcc/g++."""
		ret = ""
		for inc in includeDirs:
			ret += '-I"{}" '.format( os.path.abspath( inc ) )
		return ret


class AndroidLinker(AndroidBase, toolchain_gcc.GccLinker):
	def __init__(self, shared):
		toolchain_gcc.GccLinker.__init__(self, shared)
		AndroidBase.__init__(self)
		self._setupCompleted = False

	def copy(self, shared):
		ret = toolchain_gcc.GccLinker.copy(self, shared)
		AndroidBase._copyTo(self, ret)
		ret._setupCompleted = self._setupCompleted
		return ret

	@staticmethod
	def AdditionalArgs( parser ):
		parser.add_argument("--ndk-home", help="Location of android NDK directory")
		parser.add_argument("--sdk-home", help="Location of android SDK directory")
		parser.add_argument("--ant-home", help="Location of apache ant")
		parser.add_argument("--java-home", help="Location of java")
		parser.add_argument("--keystore", help="Location of keystore to sign release apks (default is {makefile location}/{project name}.keystore")
		parser.add_argument("--keystore-pwfile", help="Location of password file for loading keystore (default is {makefile location}/{keystore_filename}.pass)")
		parser.add_argument("--alias", help="Alias to use inside the keystore (default is project name)")
		parser.add_argument("--key-pwfile", help="Location of password file for signing release apks (default is {makefile location}/{keystore_filename}.{alias}.pass)")
		parser.add_argument("--zipalign-location", help="Location of zipalign")

	def _setupLinker(self, project):
		#TODO: Let user choose which compiler version to use; for now, using the highest numbered version.
		self._ld, self._ar = self._getCommands(project, "ld", "ar")

	def _setupForProject( self, project ):
		toolchain_gcc.GccLinker._setupForProject(self, project)
		if not self._setupCompleted:
			if "clang" in project.cc or "clang" in project.cxx:
				self.shared.isClang = True
			self._setupLinker(project)
			self._setSysRootDir(project)
			self._setupCompleted = True

			if not self.shared._keystoreLocation:
				self.shared._keystoreLocation = os.path.join(csbuild.mainFileDir, project.name+".keystore")

			if not self.shared._keystoreAlias:
				self.shared._keystoreAlias = project.name

			alias = csbuild.GetOption("alias")

			if alias:
				self.shared._keystoreAlias = alias

			if not self.shared._keystorePwFile:
				self.shared._keystorePwFile = os.path.join(csbuild.mainFileDir, self.shared._keystoreLocation+".pass")

			if not self.shared._keyPwFile:
				self.shared._keyPwFile = os.path.join(csbuild.mainFileDir, self.shared._keystoreAlias + ".keystore." + project.name + ".pass")


			ndkHome = csbuild.GetOption("ndk_home")
			sdkHome = csbuild.GetOption("sdk_home")
			antHome = csbuild.GetOption("ant_home")
			javaHome = csbuild.GetOption("java_home")
			keystore = csbuild.GetOption("keystore")
			keystorePwFile = csbuild.GetOption("keystore_pwfile")
			keyPwFile = csbuild.GetOption("key_pwfile")

			if ndkHome:
				self.shared._ndkHome = ndkHome
			if sdkHome:
				self.shared._sdkHome = sdkHome
			if antHome:
				self.shared._antHome = antHome
			if javaHome:
				self.shared._javaHome = javaHome
			if keystore:
				self.shared._keystoreLocation = keystore
			if keystorePwFile:
				self.shared._keystorePwFile = keystorePwFile
			if keyPwFile:
				self.shared._keyPwFile = keyPwFile

	def _getSystemLibDirs(self, project):
		ret = ""
		if project.hasCppFiles:
			if self.shared._stlVersion == "GNU":
				ret += "\"-l:{}\" ".format(os.path.join(
					self.shared._ndkHome,
					"sources",
					"cxx-stl",
					"gnu-libstdc++",
					"4.8",
					"libs",
					project.outputArchitecture,
					"libgnustl_static.a" if project.useStaticRuntime else "libgnustl_shared.so")
				)
			elif self.shared._stlVersion == "stlport":
				ret += "\"-l:{}\" ".format(os.path.join(
					self.shared._ndkHome,
					"sources",
					"cxx-stl",
					"stlport",
					"libs",
					project.outputArchitecture,
					"libstlport_static.a" if project.useStaticRuntime else "libstlport_shared.so")
				)
			elif self.shared._stlVersion == "libc++":
				ret += "\"-l:{}\" ".format(os.path.join(
					self.shared._ndkHome,
					"sources",
					"cxx-stl",
					"llvm-libc++",
					"libs",
					project.outputArchitecture,
					"libc++_static.a" if project.useStaticRuntime else "libc++_shared.so")
				)

		ret += '"-lc" "-lm" "-llog" "-lgcc" "-landroid" '
		ret += "--sysroot \"{}\" ".format(self.shared._sysRootDir)
		ret += "-Wl,-rpath-link=\"{}/usr/lib\" ".format(self.shared._sysRootDir)
		return ret


	def _getLibraryArg(self, lib):
		for depend in self._project_settings.reconciledLinkDepends:
			dependProj = _shared_globals.projects[depend]
			if dependProj.type == csbuild.ProjectType.Application:
				continue
			dependLibName = dependProj.outputName
			splitName = os.path.splitext(dependLibName)[0]
			if splitName == lib or splitName == "lib{}".format( lib ):
				return '\"-l:{}\" '.format( dependLibName )
		return "\"-l:{}\" ".format( self._actual_library_names[lib] )


	def GetLinkCommand( self, project, outputFile, objList ):
		self._setupForProject( project )

		linkFile = os.path.join(self._project_settings.csbuildDir, "{}.cmd".format(self._project_settings.name))

		objListData = ""
		for objFile in objList:
			objListData += '"{}" '.format( objFile )

		objListData = objListData.replace("\\", "/")
		data = objListData
		if sys.version_info >= (3, 0):
			data = data.encode("utf-8")

		file_mode = 438 # Octal 0666
		flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
		if platform.system() == "Windows":
			flags |= os.O_NOINHERIT
		fd = os.open(linkFile, flags, file_mode)
		os.write(fd, data)
		os.fsync(fd)
		os.close(fd)

		if project.type == csbuild.ProjectType.StaticLibrary:
			cmds = "\"{}\" rcs \"{}\" {}".format( self._ar, outputFile, objListData )
		else:
			if project.hasCppFiles:
				cmd = project.activeToolchain.Compiler()._settingsOverrides["cxx"]
			else:
				cmd = project.activeToolchain.Compiler()._settingsOverrides["cc"]

			libDir = os.path.join( self.shared._ndkHome, "platforms", "android-{}".format(self.shared._targetSdkVersion), "arch-{}".format(self._getSimplifiedArch(project)), "usr", "lib")

			if self.shared.isClang:
				crtbegin = os.path.join(project.objDir, "crtbegin_so.o")
				if not os.access(crtbegin, os.F_OK):
					symlink(os.path.join(libDir, "crtbegin_so.o"), crtbegin)
				crtend = os.path.join(project.objDir, "crtend_so.o")
				if not os.access(crtend, os.F_OK):
					symlink(os.path.join(libDir, "crtend_so.o"), crtend)

			if project.type == csbuild.ProjectType.SharedLibrary or project.type == csbuild.ProjectType.LoadableModule:
				sharedFlag = "-shared "
			else:
				sharedFlag = ""

			cmds = "\"{}\" -Wl,--no-undefined -fuse-ld=bfd -Wl,-z,noexecstack -Wl,-z,relro -Wl,-z,now {}-Wl,-soname,{} -o{} {} {} {}{}{} {} {}-g{} -O{} {} {} {} {} -L\"{}\"".format(
				cmd,
				"-pg " if project.profile else "",
				os.path.basename(outputFile),
				outputFile,
				"@{}".format(linkFile),
				"-Wl,--no-as-needed -Wl,--start-group" if not self.strictOrdering else "",
				self._getLibraries( project.libraries ),
				self._getStaticLibraries( project.staticLibraries ),
				self._getSharedLibraries( project.sharedLibraries ),
				"-Wl,--end-group" if not self.strictOrdering else "",
				self._getLibraryDirs( project.libraryDirs, True ),
				project.debugLevel,
				project.optLevel,
				sharedFlag,
				" ".join( project.linkerFlags ),
				self._getSystemLibDirs(project),
				self._getTargetTriple(project),
				libDir
			)

		return cmds.replace("\\", "/")

	def FindLibrary( self, project, library, libraryDirs, force_static, force_shared ):
		success = True
		out = ""
		self._setupForProject( project )
		nullOut = '"{}"'.format( os.path.join(project.csbuildDir, "null") )
		try:
			cmd = [self._ld, "-o", nullOut, "--verbose",
				   "-Bstatic" if force_static else "-Bdynamic" if force_shared else "", "-l{}".format( library ),
				   "-L", os.path.join( self.shared._ndkHome, "platforms", "android-{}".format(self.shared._targetSdkVersion), "arch-{}".format(self._getSimplifiedArch(project)), "usr", "lib")]
			cmd += shlex.split( self._getLibraryDirs( libraryDirs, False ), posix=(platform.system() != "Windows") )

			if _shared_globals.show_commands:
				print(" ".join(cmd))

			out = subprocess.check_output( cmd, stderr = subprocess.STDOUT )
		except subprocess.CalledProcessError as e:
			out = e.output
			success = False
		finally:
			if os.access(nullOut, os.F_OK):
				os.remove(nullOut)
			if sys.version_info >= (3, 0):
				RMatch = re.search( "attempt to open (.*) succeeded".encode( 'utf-8' ), out, re.I )
			else:
				RMatch = re.search( "attempt to open (.*) succeeded", out, re.I )
				#Some libraries (such as -liberty) will return successful but don't have a file (internal to ld maybe?)
			#In those cases we can probably assume they haven't been modified.
			#Set the mtime to 0 and return success as long as ld didn't return an error code.
			if RMatch is not None:
				lib = RMatch.group( 1 )
				if sys.version_info >= (3, 0):
					self._actual_library_names[library] = os.path.basename(lib).decode('utf-8')
				else:
					self._actual_library_names[library] = os.path.basename(lib)
				return lib
			elif not success:
				try:
					cmd = [self._ld, "-o", nullOut, "--verbose",
						   "-Bstatic" if force_static else "-Bdynamic" if force_shared else "", "-l:{}".format( library ),
						   "-L", os.path.join( self.shared._ndkHome, "platforms", "android-{}".format(self.shared._targetSdkVersion), "arch-{}".format(self._getSimplifiedArch(project)), "usr", "lib")]
					cmd += shlex.split( self._getLibraryDirs( libraryDirs, False ), posix=(platform.system() != "Windows") )

					if _shared_globals.show_commands:
						print(" ".join(cmd))

					out = subprocess.check_output( cmd, stderr = subprocess.STDOUT )
				except subprocess.CalledProcessError as e:
					out = e.output
					success = False
				finally:
					if os.access(nullOut, os.F_OK):
						os.remove(nullOut)
					if sys.version_info >= (3, 0):
						RMatch = re.search( "attempt to open (.*) succeeded".encode( 'utf-8' ), out, re.I )
					else:
						RMatch = re.search( "attempt to open (.*) succeeded", out, re.I )
						#Some libraries (such as -liberty) will return successful but don't have a file (internal to ld maybe?)
					#In those cases we can probably assume they haven't been modified.
					#Set the mtime to 0 and return success as long as ld didn't return an error code.
					if RMatch is not None:
						lib = RMatch.group( 1 )
						if sys.version_info >= (3, 0):
							self._actual_library_names[library] = os.path.basename(lib).decode('utf-8')
						else:
							self._actual_library_names[library] = os.path.basename(lib)
						return lib
					elif not success:
						return None

	def GetDefaultOutputExtension( self, projectType ):
		if projectType == csbuild.ProjectType.Application:
			return ""
		elif projectType == csbuild.ProjectType.StaticLibrary:
			return ".a"
		elif projectType == csbuild.ProjectType.SharedLibrary or projectType == csbuild.ProjectType.LoadableModule:
			return ".so"

class APKBuilder(AndroidBase, toolchain.toolBase):
	def __init__(self, shared):
		toolchain.toolBase.__init__(self, shared)
		AndroidBase.__init__(self)

	def copy(self, shared):
		ret = toolchain.toolBase.copy(self, shared)
		AndroidBase._copyTo(self, ret)
		return ret

	def postBuildStep(self, project):
		log.LOG_BUILD("Generating APK for {} ({} {}/{})".format(project.outputName, project.targetName, project.outputArchitecture, project.activeToolchainName))
		if project.metaType != csbuild.ProjectType.Application:
			return

		appDir = os.path.join(project.csbuildDir, "apk", project.name)
		if os.access(appDir, os.F_OK):
			shutil.rmtree(appDir)

		androidTool = os.path.join(self.shared._sdkHome, "tools", "android.bat" if platform.system() == "Windows" else "android.sh")
		cmd = [
				androidTool, "create", "project",
				"--path", appDir,
				"--target", "android-{}".format(self.shared._targetSdkVersion),
				"--name", project.name,
				"--package", "com.{}.{}".format(self.shared._packageName, project.name),
				"--activity", project.name if self.shared._activityName is None else self.shared._activityName
			]
		if _shared_globals.show_commands:
			print(cmd)
		fd = subprocess.Popen(
			cmd,
			stderr=subprocess.STDOUT,
			stdout=subprocess.PIPE
		)
		output, errors = fd.communicate()
		if fd.returncode != 0:
			log.LOG_ERROR("Android tool failed to generate project skeleton!\n{}".format(output))
			return

		libDir = ""
		if project.outputArchitecture == "x86":
			libDir = "x86"
		elif project.outputArchitecture == "mips":
			libDir = "mips"
		elif project.outputArchitecture == "armeabi":
			libDir = "armeabi"
		elif project.outputArchitecture == "armeabi-v7a-hard":
			libDir = "armeabi-v7a-hard"
		else:
			libDir = "armeabi-v7a"

		libDir = os.path.join(appDir, "libs", libDir)

		if not os.access(libDir, os.F_OK):
			os.makedirs(libDir)

		for library in project.libraryLocations:
			if sys.version_info >= ( 3, 0 ):
				library = library.decode( "utf-8" )
			#don't copy android system libraries
			if library.startswith(self.shared._ndkHome):
				continue
			shutil.copyfile(library, os.path.join(libDir, os.path.basename(library)))

		for dep in project.reconciledLinkDepends:
			depProj = _shared_globals.projects[dep]
			libFile = os.path.join(depProj.outputDir, depProj.outputName)
			shutil.copyfile(libFile, os.path.join(libDir, os.path.basename(libFile)))

		shutil.copyfile(os.path.join(project.outputDir, project.outputName), os.path.join(libDir, os.path.basename(project.outputName)))

		with open(os.path.join(appDir, "AndroidManifest.xml"), "w") as f:
			f.write('<?xml version="1.0" encoding="utf-8"?>\n')
			f.write('<manifest xmlns:android="http://schemas.android.com/apk/res/android"\n')
			f.write('  package="com.{}.{}"\n'.format(self.shared._packageName, project.name))
			f.write('  android:versionCode="1"\n')
			f.write('  android:versionName="1.0">\n')
			f.write('  <uses-sdk android:minSdkVersion="{}" android:targetSdkVersion="{}"/>\n'.format(self.shared._minSdkVersion, self.shared._targetSdkVersion))
			for feature in self.shared._usedFeatures:
				#example: android:glEsVersion=\"0x00020000\"
				f.write('  <uses-feature android{}></uses-feature>'.format(feature))
			for permission in self.shared._usedPermissions:
				f.write('  <uses-permission android:name="android.permission.{}"/>\n'.format(permission))
			f.write('  <application android:label="@string/app_name" android:hasCode="false" android:debuggable="true">\n')
			f.write('    <activity android:name="android.app.NativeActivity"\n')
			f.write('      android:label="@string/app_name"\n'.format(project.name))
			f.write('      android:configChanges="orientation|keyboardHidden">\n')
			f.write('      <meta-data android:name="android.app.lib_name" android:value="{}"/>\n'.format(project.outputName[3:-3]))
			f.write('      <intent-filter>\n"')
			f.write('        <action android:name="android.intent.action.MAIN"/>\n')
			f.write('        <category android:name="android.intent.category.LAUNCHER"/>\n')
			f.write('      </intent-filter>\n')
			f.write('    </activity>\n')
			f.write('  </application>\n')
			f.write('</manifest>\n')

		if self.IsAndroidDebugBuild( project ):
			antBuildType = "debug"
		else:
			antBuildType = "release"

		cmd = [
				os.path.join(self.shared._antHome, "bin", "ant.bat" if platform.system() == "Windows" else "ant.sh"),
				antBuildType
			]
		if _shared_globals.show_commands:
			print(cmd)

		fd = subprocess.Popen(
			cmd,
			stderr=subprocess.STDOUT,
			stdout=subprocess.PIPE,
			cwd=appDir
		)

		output, errors = fd.communicate()
		if fd.returncode != 0:
			log.LOG_ERROR("Ant build failed!\n{}".format(output))
			return

		appNameBase = "{}-{}".format(project.outputName[3:-3], antBuildType)
		appName = appNameBase + ".apk"
		appStartLoc = os.path.join(appDir, "bin", appName)

		if antBuildType == "release":
			appNameUnsigned = appNameBase + "-unsigned.apk"
			appUnsignedLoc = os.path.join(appDir, "bin", appNameUnsigned)
			with open(self.shared._keystorePwFile, "r") as f:
				storePass = f.read().strip()
			if os.access(self.shared._keyPwFile, os.F_OK):
				with open(self.shared._keyPwFile, "r") as f:
					keyPass = f.read().strip()
			else:
				keyPass = storePass

			log.LOG_BUILD("Signing {} with key {}...".format(appName, self.shared._keystoreLocation))

			jarsigner = os.path.join(self.shared._javaHome, "bin", "jarsigner{}".format(".exe" if platform.system() == "Windows" else ""))
			cmd = [
					jarsigner,
					"-sigalg", "SHA1withRSA",
					"-digestalg", "SHA1",
					"-keystore", self.shared._keystoreLocation,
					"-storepass", storePass,
					"-keypass", keyPass,
					appUnsignedLoc,
					self.shared._keystoreAlias
				]
			if _shared_globals.show_commands:
				print(cmd)

			fd = subprocess.Popen(
				cmd,
				stderr=subprocess.STDOUT,
				stdout=subprocess.PIPE,
				cwd=appDir
			)

			output, errors = fd.communicate()
			if fd.returncode != 0:
				log.LOG_ERROR("Signing failed!\n{}".format(output))
				return

			log.LOG_BUILD("Zip-Aligning {}...".format(appName, self.shared._keystoreLocation))

			zipalign = os.path.join(self.shared._sdkHome, "tools", "zipalign{}".format(".exe" if platform.system() == "Windows" else ""))
			cmd = [
					zipalign,
					"-v", "4",
					appUnsignedLoc,
					appStartLoc
				]
			if _shared_globals.show_commands:
				print(cmd)
			fd = subprocess.Popen(
				cmd,
				stderr=subprocess.STDOUT,
				stdout=subprocess.PIPE,
				cwd=appDir
			)

			output, errors = fd.communicate()
			if fd.returncode != 0:
				log.LOG_ERROR("Zipalign failed!\n{}".format(output))
				return

		appEndLoc = os.path.join(project.outputDir, appName)
		if os.access(appEndLoc, os.F_OK):
			os.remove(appEndLoc)

		shutil.move(appStartLoc, project.outputDir)
		log.LOG_BUILD("Finished generating APK for {} ({} {}/{})".format(project.outputName, project.targetName, project.outputArchitecture, project.activeToolchainName))
