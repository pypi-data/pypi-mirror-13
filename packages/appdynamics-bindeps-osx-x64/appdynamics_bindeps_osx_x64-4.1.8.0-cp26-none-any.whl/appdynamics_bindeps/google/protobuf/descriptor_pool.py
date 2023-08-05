# Protocol Buffers - Google's data interchange format
# Copyright 2008 Google Inc.  All rights reserved.
# http://code.google.com/p/protobuf/
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Provides DescriptorPool to use as a container for proto2 descriptors.

The DescriptorPool is used in conjection with a DescriptorDatabase to maintain
a collection of protocol buffer descriptors for use when dynamically creating
message types at runtime.

For most applications protocol buffers should be used via modules generated by
the protocol buffer compiler tool. This should only be used when the type of
protocol buffers used in an application or library cannot be predetermined.

Below is a straightforward example on how to use this class:

  pool = DescriptorPool()
  file_descriptor_protos = [ ... ]
  for file_descriptor_proto in file_descriptor_protos:
    pool.Add(file_descriptor_proto)
  my_message_descriptor = pool.FindMessageTypeByName('some.package.MessageType')

The message descriptor can be used in conjunction with the message_factory
module in order to create a protocol buffer class that can be encoded and
decoded.
"""

__author__ = 'matthewtoia@google.com (Matt Toia)'

from appdynamics_bindeps.google.protobuf import descriptor_pb2
from appdynamics_bindeps.google.protobuf import descriptor
from appdynamics_bindeps.google.protobuf import descriptor_database


class DescriptorPool(object):
  """A collection of protobufs dynamically constructed by descriptor protos."""

  def __init__(self, descriptor_db=None):
    """Initializes a Pool of proto buffs.

    The descriptor_db argument to the constructor is provided to allow
    specialized file descriptor proto lookup code to be triggered on demand. An
    example would be an implementation which will read and compile a file
    specified in a call to FindFileByName() and not require the call to Add()
    at all. Results from this database will be cached internally here as well.

    Args:
      descriptor_db: A secondary source of file descriptors.
    """

    self._internal_db = descriptor_database.DescriptorDatabase()
    self._descriptor_db = descriptor_db
    self._descriptors = {}
    self._enum_descriptors = {}
    self._file_descriptors = {}

  def Add(self, file_desc_proto):
    """Adds the FileDescriptorProto and its types to this pool.

    Args:
      file_desc_proto: The FileDescriptorProto to add.
    """

    self._internal_db.Add(file_desc_proto)

  def FindFileByName(self, file_name):
    """Gets a FileDescriptor by file name.

    Args:
      file_name: The path to the file to get a descriptor for.

    Returns:
      A FileDescriptor for the named file.

    Raises:
      KeyError: if the file can not be found in the pool.
    """

    try:
      file_proto = self._internal_db.FindFileByName(file_name)
    except KeyError as error:
      if self._descriptor_db:
        file_proto = self._descriptor_db.FindFileByName(file_name)
      else:
        raise error
    if not file_proto:
      raise KeyError('Cannot find a file named %s' % file_name)
    return self._ConvertFileProtoToFileDescriptor(file_proto)

  def FindFileContainingSymbol(self, symbol):
    """Gets the FileDescriptor for the file containing the specified symbol.

    Args:
      symbol: The name of the symbol to search for.

    Returns:
      A FileDescriptor that contains the specified symbol.

    Raises:
      KeyError: if the file can not be found in the pool.
    """

    try:
      file_proto = self._internal_db.FindFileContainingSymbol(symbol)
    except KeyError as error:
      if self._descriptor_db:
        file_proto = self._descriptor_db.FindFileContainingSymbol(symbol)
      else:
        raise error
    if not file_proto:
      raise KeyError('Cannot find a file containing %s' % symbol)
    return self._ConvertFileProtoToFileDescriptor(file_proto)

  def FindMessageTypeByName(self, full_name):
    """Loads the named descriptor from the pool.

    Args:
      full_name: The full name of the descriptor to load.

    Returns:
      The descriptor for the named type.
    """

    full_name = full_name.lstrip('.')  # fix inconsistent qualified name formats
    if full_name not in self._descriptors:
      self.FindFileContainingSymbol(full_name)
    return self._descriptors[full_name]

  def FindEnumTypeByName(self, full_name):
    """Loads the named enum descriptor from the pool.

    Args:
      full_name: The full name of the enum descriptor to load.

    Returns:
      The enum descriptor for the named type.
    """

    full_name = full_name.lstrip('.')  # fix inconsistent qualified name formats
    if full_name not in self._enum_descriptors:
      self.FindFileContainingSymbol(full_name)
    return self._enum_descriptors[full_name]

  def _ConvertFileProtoToFileDescriptor(self, file_proto):
    """Creates a FileDescriptor from a proto or returns a cached copy.

    This method also has the side effect of loading all the symbols found in
    the file into the appropriate dictionaries in the pool.

    Args:
      file_proto: The proto to convert.

    Returns:
      A FileDescriptor matching the passed in proto.
    """

    if file_proto.name not in self._file_descriptors:
      file_descriptor = descriptor.FileDescriptor(
          name=file_proto.name,
          package=file_proto.package,
          options=file_proto.options,
          serialized_pb=file_proto.SerializeToString())
      scope = {}
      dependencies = list(self._GetDeps(file_proto))

      for dependency in dependencies:
        dep_desc = self.FindFileByName(dependency.name)
        dep_proto = descriptor_pb2.FileDescriptorProto.FromString(
            dep_desc.serialized_pb)
        package = '.' + dep_proto.package
        package_prefix = package + '.'

        def _strip_package(symbol):
          if symbol.startswith(package_prefix):
            return symbol[len(package_prefix):]
          return symbol

        symbols = list(self._ExtractSymbols(dep_proto.message_type, package))
        scope.update(symbols)
        scope.update((_strip_package(k), v) for k, v in symbols)

        symbols = list(self._ExtractEnums(dep_proto.enum_type, package))
        scope.update(symbols)
        scope.update((_strip_package(k), v) for k, v in symbols)

      for message_type in file_proto.message_type:
        message_desc = self._ConvertMessageDescriptor(
            message_type, file_proto.package, file_descriptor, scope)
        file_descriptor.message_types_by_name[message_desc.name] = message_desc
      for enum_type in file_proto.enum_type:
        self._ConvertEnumDescriptor(enum_type, file_proto.package,
                                    file_descriptor, None, scope)
      for desc_proto in self._ExtractMessages(file_proto.message_type):
        self._SetFieldTypes(desc_proto, scope)

      for desc_proto in file_proto.message_type:
        desc = scope[desc_proto.name]
        file_descriptor.message_types_by_name[desc_proto.name] = desc
      self.Add(file_proto)
      self._file_descriptors[file_proto.name] = file_descriptor

    return self._file_descriptors[file_proto.name]

  def _ConvertMessageDescriptor(self, desc_proto, package=None, file_desc=None,
                                scope=None):
    """Adds the proto to the pool in the specified package.

    Args:
      desc_proto: The descriptor_pb2.DescriptorProto protobuf message.
      package: The package the proto should be located in.
      file_desc: The file containing this message.
      scope: Dict mapping short and full symbols to message and enum types.

    Returns:
      The added descriptor.
    """

    if package:
      desc_name = '.'.join((package, desc_proto.name))
    else:
      desc_name = desc_proto.name

    if file_desc is None:
      file_name = None
    else:
      file_name = file_desc.name

    if scope is None:
      scope = {}

    nested = [
        self._ConvertMessageDescriptor(nested, desc_name, file_desc, scope)
        for nested in desc_proto.nested_type]
    enums = [
        self._ConvertEnumDescriptor(enum, desc_name, file_desc, None, scope)
        for enum in desc_proto.enum_type]
    fields = [self._MakeFieldDescriptor(field, desc_name, index)
              for index, field in enumerate(desc_proto.field)]
    extensions = [self._MakeFieldDescriptor(extension, desc_name, True)
                  for index, extension in enumerate(desc_proto.extension)]
    extension_ranges = [(r.start, r.end) for r in desc_proto.extension_range]
    if extension_ranges:
      is_extendable = True
    else:
      is_extendable = False
    desc = descriptor.Descriptor(
        name=desc_proto.name,
        full_name=desc_name,
        filename=file_name,
        containing_type=None,
        fields=fields,
        nested_types=nested,
        enum_types=enums,
        extensions=extensions,
        options=desc_proto.options,
        is_extendable=is_extendable,
        extension_ranges=extension_ranges,
        file=file_desc,
        serialized_start=None,
        serialized_end=None)
    for nested in desc.nested_types:
      nested.containing_type = desc
    for enum in desc.enum_types:
      enum.containing_type = desc
    scope[desc_proto.name] = desc
    scope['.' + desc_name] = desc
    self._descriptors[desc_name] = desc
    return desc

  def _ConvertEnumDescriptor(self, enum_proto, package=None, file_desc=None,
                             containing_type=None, scope=None):
    """Make a protobuf EnumDescriptor given an EnumDescriptorProto protobuf.

    Args:
      enum_proto: The descriptor_pb2.EnumDescriptorProto protobuf message.
      package: Optional package name for the new message EnumDescriptor.
      file_desc: The file containing the enum descriptor.
      containing_type: The type containing this enum.
      scope: Scope containing available types.

    Returns:
      The added descriptor
    """

    if package:
      enum_name = '.'.join((package, enum_proto.name))
    else:
      enum_name = enum_proto.name

    if file_desc is None:
      file_name = None
    else:
      file_name = file_desc.name

    values = [self._MakeEnumValueDescriptor(value, index)
              for index, value in enumerate(enum_proto.value)]
    desc = descriptor.EnumDescriptor(name=enum_proto.name,
                                     full_name=enum_name,
                                     filename=file_name,
                                     file=file_desc,
                                     values=values,
                                     containing_type=containing_type,
                                     options=enum_proto.options)
    scope[enum_proto.name] = desc
    scope['.%s' % enum_name] = desc
    self._enum_descriptors[enum_name] = desc
    return desc

  def _MakeFieldDescriptor(self, field_proto, message_name, index,
                           is_extension=False):
    """Creates a field descriptor from a FieldDescriptorProto.

    For message and enum type fields, this method will do a look up
    in the pool for the appropriate descriptor for that type. If it
    is unavailable, it will fall back to the _source function to
    create it. If this type is still unavailable, construction will
    fail.

    Args:
      field_proto: The proto describing the field.
      message_name: The name of the containing message.
      index: Index of the field
      is_extension: Indication that this field is for an extension.

    Returns:
      An initialized FieldDescriptor object
    """

    if message_name:
      full_name = '.'.join((message_name, field_proto.name))
    else:
      full_name = field_proto.name

    return descriptor.FieldDescriptor(
        name=field_proto.name,
        full_name=full_name,
        index=index,
        number=field_proto.number,
        type=field_proto.type,
        cpp_type=None,
        message_type=None,
        enum_type=None,
        containing_type=None,
        label=field_proto.label,
        has_default_value=False,
        default_value=None,
        is_extension=is_extension,
        extension_scope=None,
        options=field_proto.options)

  def _SetFieldTypes(self, desc_proto, scope):
    """Sets the field's type, cpp_type, message_type and enum_type.

    Args:
      desc_proto: The message descriptor to update.
      scope: Enclosing scope of available types.
    """

    desc = scope[desc_proto.name]
    for field_proto, field_desc in zip(desc_proto.field, desc.fields):
      if field_proto.type_name:
        type_name = field_proto.type_name
        if type_name not in scope:
          type_name = '.' + type_name
        desc = scope[type_name]
      else:
        desc = None

      if not field_proto.HasField('type'):
        if isinstance(desc, descriptor.Descriptor):
          field_proto.type = descriptor.FieldDescriptor.TYPE_MESSAGE
        else:
          field_proto.type = descriptor.FieldDescriptor.TYPE_ENUM

      field_desc.cpp_type = descriptor.FieldDescriptor.ProtoTypeToCppProtoType(
          field_proto.type)

      if (field_proto.type == descriptor.FieldDescriptor.TYPE_MESSAGE
          or field_proto.type == descriptor.FieldDescriptor.TYPE_GROUP):
        field_desc.message_type = desc

      if field_proto.type == descriptor.FieldDescriptor.TYPE_ENUM:
        field_desc.enum_type = desc

      if field_proto.label == descriptor.FieldDescriptor.LABEL_REPEATED:
        field_desc.has_default = False
        field_desc.default_value = []
      elif field_proto.HasField('default_value'):
        field_desc.has_default = True
        if (field_proto.type == descriptor.FieldDescriptor.TYPE_DOUBLE or
            field_proto.type == descriptor.FieldDescriptor.TYPE_FLOAT):
          field_desc.default_value = float(field_proto.default_value)
        elif field_proto.type == descriptor.FieldDescriptor.TYPE_STRING:
          field_desc.default_value = field_proto.default_value
        elif field_proto.type == descriptor.FieldDescriptor.TYPE_BOOL:
          field_desc.default_value = field_proto.default_value.lower() == 'true'
        elif field_proto.type == descriptor.FieldDescriptor.TYPE_ENUM:
          field_desc.default_value = field_desc.enum_type.values_by_name[
              field_proto.default_value].index
        else:
          field_desc.default_value = int(field_proto.default_value)
      else:
        field_desc.has_default = False
        field_desc.default_value = None

      field_desc.type = field_proto.type

    for nested_type in desc_proto.nested_type:
      self._SetFieldTypes(nested_type, scope)

  def _MakeEnumValueDescriptor(self, value_proto, index):
    """Creates a enum value descriptor object from a enum value proto.

    Args:
      value_proto: The proto describing the enum value.
      index: The index of the enum value.

    Returns:
      An initialized EnumValueDescriptor object.
    """

    return descriptor.EnumValueDescriptor(
        name=value_proto.name,
        index=index,
        number=value_proto.number,
        options=value_proto.options,
        type=None)

  def _ExtractSymbols(self, desc_protos, package):
    """Pulls out all the symbols from descriptor protos.

    Args:
      desc_protos: The protos to extract symbols from.
      package: The package containing the descriptor type.
    Yields:
      A two element tuple of the type name and descriptor object.
    """

    for desc_proto in desc_protos:
      if package:
        message_name = '.'.join((package, desc_proto.name))
      else:
        message_name = desc_proto.name
      message_desc = self.FindMessageTypeByName(message_name)
      yield (message_name, message_desc)
      for symbol in self._ExtractSymbols(desc_proto.nested_type, message_name):
        yield symbol
      for symbol in self._ExtractEnums(desc_proto.enum_type, message_name):
        yield symbol

  def _ExtractEnums(self, enum_protos, package):
    """Pulls out all the symbols from enum protos.

    Args:
      enum_protos: The protos to extract symbols from.
      package: The package containing the enum type.

    Yields:
      A two element tuple of the type name and enum descriptor object.
    """

    for enum_proto in enum_protos:
      if package:
        enum_name = '.'.join((package, enum_proto.name))
      else:
        enum_name = enum_proto.name
      enum_desc = self.FindEnumTypeByName(enum_name)
      yield (enum_name, enum_desc)

  def _ExtractMessages(self, desc_protos):
    """Pulls out all the message protos from descriptos.

    Args:
      desc_protos: The protos to extract symbols from.

    Yields:
      Descriptor protos.
    """

    for desc_proto in desc_protos:
      yield desc_proto
      for message in self._ExtractMessages(desc_proto.nested_type):
        yield message

  def _GetDeps(self, file_proto):
    """Recursively finds dependencies for file protos.

    Args:
      file_proto: The proto to get dependencies from.

    Yields:
      Each direct and indirect dependency.
    """

    for dependency in file_proto.dependency:
      dep_desc = self.FindFileByName(dependency)
      dep_proto = descriptor_pb2.FileDescriptorProto.FromString(
          dep_desc.serialized_pb)
      yield dep_proto
      for parent_dep in self._GetDeps(dep_proto):
        yield parent_dep
