"""
cake : metabuild for c/c++
"""

import os
import re
import sys
import logging
from glob import glob
from collections import namedtuple,OrderedDict
from subprocess import check_output

"""
configuration

cake maintains several "first class" entities:
  * c compiler,
  * c++ compiler,
  * linker (usually the c/c++ compiler with special flags)
  * archiver

each of these has a name and a set of associated flags.

Target (static, shared, exec, etc) typically will use one of
these major commands, and override flags as needed.

Custom commands will provide their own command, but flags
for these are not overridable.
"""

CAKEFILE = "Cakefile"

CC = "cc"
CXX = "cxx"
LD = "ld"
AR = "ar"

VARIABLES = OrderedDict([
  ("AR" , "ar"),
  ("ARFLAGS" , "-rv"),
  ("CC" , "gcc"),
  ("CFLAGS" , ""),
  ("CXX" , "g++"),
  ("CXXFLAGS" , ""),
  ("LD" , "ref(CC)"),
  ("LDFLAGS", ""),
  ("LIB_DIRS" , ""),
  ("LIBS" , "")
])

FLAGS_VARS = {
  CC : "CFLAGS",
  CXX : "CXXFLAGS"
}

LIB_LDFLAGS = {
  "static" : "",
  "shared" : "--shared"
}

LIB_FLAGS = {
  "static" : ["-c"],
  "shared" : ["-c", "-fPIC"]
}

# NOTE: IN and OUT are special variables for all backends
COMMANDS = {
  "cc" : "ref(CC) ref(CFLAGS) ref(IN) -o ref(OUT)",
  "cxx" : "ref(CXX) ref(CXXFLAGS) ref(IN) -o ref(OUT)",
  "ld" : "ref(LD) ref(LDFLAGS) ref(IN) -o ref(OUT) ref(LIB_DIRS) ref(LIBS)",
  "ar" : "ref(AR) ref(ARFLAGS) ref(OUT) ref(IN)"
}

"""
internal build representation
"""

Target = namedtuple("Target", [
  "output",     # literally, the file (just one, for now) produced
  "sources",    # inputs that should be passed to the command
  "depends",    # connections in the dependency graph
  "command",    # the command to evaluate this target
  "variables",  # overridden variables
])

"""
utils
"""

class Logger:

  def __init__(self):
    self._types = {
      "static", "shared", "object", "executable", "target", "command"
    }
    self._logs = {
      "info", "warn"
    }

  def _log(self, __name, fmt, **kwargs):
    print("{name} - {message}".format(
      name=__name, message=fmt.format(**kwargs)))

  def error(self, fmt, **kwargs):
    self._log("ERROR", fmt, **kwargs)
    sys.exit(1)

  def __getattr__(self, name):
    if name in self._types:
      return lambda val: self._log(name.upper(),
        "{output}", output=val.output)
    if name in self._logs:
      return lambda fmt, **kwargs: self._log(
        name.upper(), fmt, **kwargs)
    raise AttributeError(name)

def merge(*objs, **kwargs):
  res = {}
  for o in list(objs) + [kwargs]:
    for k,v in o.items():
      res[k] = v
  return res

def slist(root, args, splat=False, exist=False):
  """
  source list, normalizes args to a list of strings
  """
  if args is None:
    return []
  if isinstance(args, str):
    args = [args]
  elif not isinstance(args, (list, tuple)):
    raise ValueError("expected str,list,tuple, got {tp} ({val})".format(
      tp=type(args), val=args))
  res = []
  for a in args:
    full = os.path.abspath(
      os.path.join(root, a))
    if splat:
      res += glob(full)
    else:
      if exist and not os.path.exists(a):
        log.error("path {p} does not exist ({full})",
          p=a, full=full)
      res.append(full)
  return res

def strlist(args):
  """
  normalizes input to a list of strings
  """
  if args is None:
    return []
  if isinstance(args, str):
    return [args]
  if not isinstance(args, (list, tuple)):
    raise ValueError("expected str,list,tuple, got {tp} ({val})".format(
      tp=type(args), val=args))
  return list(args)

def choose_compiler(path):
  _,ext = os.path.splitext(path)
  source_exts = {
    ".c" : CC,
    ".cc" : CXX,
    ".cxx" : CXX,
    ".cpp" : CXX
  }
  if ext not in source_exts:
    log.error("unknown source {src}", src=path)
  return source_exts[ext]

def which(ex):
  p = check_output("which {ex}".format(ex=ex), shell=True)
  return p.decode().strip()

"""
non-context api calls
"""

def api_c_compiler(name, path=None):
  full = which(name)
  if full is None:
    log.error("unable to find c compiler {name} "
      "try providing path=...", name=name)
  VARIABLES["CC"] = full

def api_cxx_compiler(name, path=None):
  full = which(name)
  if full is None:
    log.error("unable to find cxx compiler {name} "
      "try providing path=...", name=name)
  VARIABLES["CXX"] = full

"""
cake context
"""

class Cake:

  def __init__(self, root, generator, build):
    self._root = root
    self._dirs = [root]
    self._generator = generator
    self._build = build
    self._targets = []
    self.local_vars = {}

  def push_dir(self, path):
    full = os.path.abspath(
      os.path.join(self.current_dir, path))
    self._dirs.append(full)

  def pop_dir(self):
    if len(self._dirs) > 1:
      self._dirs.pop()

  @property
  def current_dir(self):
    return self._dirs[-1]

  @property
  def current_file(self):
    return os.path.join(self.current_dir, CAKEFILE)

  def api_lib(self,
    lib_type, command,
    name,
    includes=None,
    sources=None,
    depends=None,
    **kwargs):

    """
    name : will be its own file in this relative dir in build root
    includes : string or list, dirs to include
    sources : string or list (splat optional) sources
    depends : other targets or names that must be built first
    """

    incs = slist(self.current_dir, includes, splat=False, exist=False)
    srcs = slist(self.current_dir, sources, splat=True, exist=True)
    deps = strlist(depends)

    if len(srcs) == 0:
      log.error("{ltype} {name} source expression {sxp} "
        "resolved to 0 source files", 
        ltype=lib_type, name=name, sxp=sources)

    if len(deps) != 0:
      log.error("{ltype} lib {name} : depdencies are not implemented",
        ltype=lib_type, name=name)

    rel = os.path.relpath(self.current_dir, self._root)

    objs = []
    for s in srcs:

      obj = os.path.abspath(
        os.path.join(rel, "{lname}_{name}.o".format(
          lname=name, name=os.path.basename(s))))

      c = choose_compiler(s)
      flags_var = FLAGS_VARS[c]

      flags = ["ref({fv})".format(fv=flags_var)] + \
        ["-I{inc}".format(inc=i) for i in incs] +  \
        LIB_FLAGS[lib_type]

      variables = {
        flags_var : " ".join(flags)
      }

      for k,v in kwargs.items():
        if k in variables:
          variables[k] = " ".join(
            [variables[k], v])
        else:
          variables[k] = v

      st = Target(obj, [s], [], c, variables)
      self._targets.append(st)
      objs.append(obj)

    outp = os.path.abspath(
      os.path.join(rel, name))

    variables = {
      "LDFLAGS" : LIB_LDFLAGS[lib_type]
    }

    t = Target(outp,objs,deps,command,variables)
    lcall = getattr(log, lib_type)
    lcall(t)
    self._targets.append(t)

    return t

  def api_executable(self,
    name,
    includes=None,
    sources=None,
    depends=None,
    libdirs=None,
    libs=None,
    **kwargs):

    """
    name : will be its own file in this relative dir in build root
    includes : string or list, dirs to include
    sources : string or list (splat optional) sources
    depends : other targets or names that must be built first
    libdirs : include dirs, but for libraries
    libs : string or list, libraries to link against
    """

    incs = slist(self.current_dir, includes, splat=False, exist=False)
    srcs = slist(self.current_dir, sources, splat=True, exist=True)
    libd = slist(self.current_dir, libdirs, splat=False, exist=False)
    deps = strlist(depends)
    libdirs = strlist(libdirs)

    if not isinstance(libs, list):
      libs = [libs]

    if len(srcs) == 0:
      log.error("executable {name} source expression {sxp} "
        "resolved to 0 source files", 
        name=name, sxp=sources)

    if len(deps) != 0:
      log.error("executable lib {name} : depdencies are not implemented",
        name=name)

    rel = os.path.relpath(self.current_dir, self._root)

    objs = []
    for s in srcs:

      obj = os.path.abspath(
        os.path.join(rel, "{ename}_{name}.o".format(
          ename=name, name=os.path.basename(s))))

      c = choose_compiler(s)
      flags_var = FLAGS_VARS[c]

      flags = ["ref({fv})".format(fv=flags_var)] + \
        ["-I{inc}".format(inc=i) for i in incs] + \
        ["-c"] # executable objects still need to be built in this mode

      variables = {
        flags_var : " ".join(flags)
      }

      for k,v in kwargs.items():
        if k in variables:
          variables[k] = " ".join(
            [variables[k], v])
        else:
          variables[k] = v

      st = Target(obj, [s], [], c, variables)
      self._targets.append(st)
      objs.append(obj)

    outp = os.path.abspath(
      os.path.join(rel, name))

    ld_dirs = []
    ld_libs = []
    exec_depends = []

    for l in libs:
      print(l)
      if isinstance(l, Target):
        objs.append(l.output)
        exec_depends.append(l.output)
      else:
        ld_libs.append(l)

    for l in libdirs:
      ld_dirs.append(l)

    for d in deps:
      exec_depends.append(d)

    variables = {
      "LIB_DIRS" : " ".join(["-L{l}".format(l=l) for l in ld_dirs]),
      "LIBS" : " ".join(["-l{l}".format(l=l) for l in ld_libs])
    }

    t = Target(outp,objs,exec_depends,LD,variables)
    log.executable(t)
    self._targets.append(t)

    return t

  def write(self, out):

    """
    out : backend instance to write to
    serialize the context to the output
    """

    for v,val in VARIABLES.items():
      out.define(v, val)

    out.compiler(CC, COMMANDS[CC])
    out.compiler(CXX, COMMANDS[CXX])
    out.command(LD, COMMANDS[LD])
    out.command(AR, COMMANDS[AR])

    for t in self._targets:
      out.target(*t)

"""
the parent cake entry point
"""

def enter_cake(root, generator, build):

  def cakefile(cake, rel_path):

    """
    loads a single cakefile and adds to
    the running context
    """

    if rel_path is not None:
      cake.push_dir(rel_path)

    if not os.path.exists(cake.current_file):
      log.error("{rel} has no {cf} (expected {full})",
        rel=rel_path, cf=CAKEFILE, full=cake.current_file)

    log.info("loading {cf}", cf=cake.current_file)

    api_vars = {
      "c_compiler" : api_c_compiler,
      "cxx_compiler" : api_cxx_compiler,
      "static" : lambda name, **kwargs: cake.api_lib("static", AR, name, **kwargs),
      "shared" : lambda name, **kwargs: cake.api_lib("shared", LD, name, **kwargs),
      "executable" : cake.api_executable,
      "subdir" : lambda path: cakefile(cake, path)
    }

    local_vars = merge(api_vars, cake.local_vars)

    with open(cake.current_file, "r") as fd:
      src = fd.read()

    obj = compile(src, cake.current_file, "exec")
    exec(obj, {}, local_vars)

    for k,v in local_vars.items():
      if k not in api_vars:
        cake.local_vars[k] = v

    if rel_path is not None:
      cake.pop_dir()

  cake = Cake(root, generator, build)
  cakefile(cake, None)

  outfiles = {
    "ninja" : "build.ninja",
    "make" : "Makefile"
  }

  outtypes = {
    "ninja" : Ninjabuild,
    "make" : Makefile
  }

  with open(outfiles[generator], "w") as fd:
    out = outtypes[generator](fd)
    cake.write(out)

  log.info("wrote {file}", file=outfiles[generator])

"""
command line interface
"""

def main():

  from argparse import ArgumentParser
  p = ArgumentParser()
  p.add_argument(
    "-b","--build",
    help="build type",
    choices=["debug", "release"],
    default="debug")
  p.add_argument(
    "-g","--generator",
    help="backend generator",
    choices=["ninja","make"],
    default="ninja")
  p.add_argument(
    "cake_root",
    help="directory containing parent {cf}".format(cf=CAKEFILE))
  args = p.parse_args()
  args.cake_root = os.path.abspath(args.cake_root)

  global log
  log = Logger()

  if os.path.exists(
      os.path.join(os.getcwd(), CAKEFILE)):
    log.error("cannot build in a directory with a {cf}"
      " please create a separate build directory", cf=CAKEFILE)

  enter_cake(
    root=args.cake_root,
    generator=args.generator,
    build=args.build)

"""
backends
"""

class Ninjabuild:

  @staticmethod
  def _deref(val):
    rep = re.sub("ref\((\w+)\)",
      lambda m: "${v}".format(v=m.group(1)),
      val)
    rep = rep.replace("$OUT", "$out")
    rep = rep.replace("$IN", "$in")
    if rep == val:
      return rep
    else:
      return Ninjabuild._deref(rep)

  def __init__(self, fd):
    self._fd = fd

  def define(self, key, value):
    self._fd.write("{key} = {value}\n".format(
      key=key, value=Ninjabuild._deref(value)))

  def compiler(self, name, command):
    self._fd.write("rule {name}\n"
      "  command = {command}\n"
      "  description = {name} $out\n"
      "  depfile = $out.d\n"
      "  deps = gcc\n".format(
      name=name,
      command=self._deref(command)))

  def command(self, name, command):
    self._fd.write("rule {name}\n"
      "  command = {command}\n"
      "  description = {name} $out\n".format(
      name=name,
      command=self._deref(command)))

  def target(self, out, sources, depends, command, variables={}):
    self._fd.write("build {out}: {command} {sources} | {depends}\n".format(
      out=out,
      command=command,
      sources=" ".join(sources),
      depends=" ".join(depends)))
    for v,val in variables.items():
      self._fd.write("  {name} = {value}\n".format(
        name=v, value=self._deref(val)))

class Makefile:
 
  def __init__(self, fd):
    raise NotImplementedError()

