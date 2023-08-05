# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: EPType.proto

from appdynamics_bindeps.google.protobuf.internal import enum_type_wrapper
from appdynamics_bindeps.google.protobuf import descriptor as _descriptor
from appdynamics_bindeps.google.protobuf import message as _message
from appdynamics_bindeps.google.protobuf import reflection as _reflection
from appdynamics_bindeps.google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='EPType.proto',
  package='appdynamics.pb.Agent',
  serialized_pb='\n\x0c\x45PType.proto\x12\x14\x61ppdynamics.pb.Agent*\xa4\x01\n\x0e\x45ntryPointType\x12\x0b\n\x07PHP_WEB\x10\x00\x12\x0b\n\x07PHP_MVC\x10\x01\x12\x0e\n\nPHP_DRUPAL\x10\x02\x12\x11\n\rPHP_WORDPRESS\x10\x03\x12\x0b\n\x07PHP_CLI\x10\x04\x12\x13\n\x0fPHP_WEB_SERVICE\x10\x05\x12\x0e\n\nNODEJS_WEB\x10\x06\x12\n\n\x06NATIVE\x10\x07\x12\x0e\n\nPYTHON_WEB\x10\x08\x12\x07\n\x03WEB\x10\t*t\n\rExitPointType\x12\r\n\tEXIT_HTTP\x10\x00\x12\x0b\n\x07\x45XIT_DB\x10\x01\x12\x0e\n\nEXIT_CACHE\x10\x02\x12\x11\n\rEXIT_RABBITMQ\x10\x03\x12\x13\n\x0f\x45XIT_WEBSERVICE\x10\x04\x12\x0f\n\x0b\x45XIT_CUSTOM\x10\x05\x42\x10\n\x0e\x61ppdynamics.pb')

_ENTRYPOINTTYPE = _descriptor.EnumDescriptor(
  name='EntryPointType',
  full_name='appdynamics.pb.Agent.EntryPointType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PHP_WEB', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PHP_MVC', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PHP_DRUPAL', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PHP_WORDPRESS', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PHP_CLI', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PHP_WEB_SERVICE', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NODEJS_WEB', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NATIVE', index=7, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PYTHON_WEB', index=8, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WEB', index=9, number=9,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=39,
  serialized_end=203,
)

EntryPointType = enum_type_wrapper.EnumTypeWrapper(_ENTRYPOINTTYPE)
_EXITPOINTTYPE = _descriptor.EnumDescriptor(
  name='ExitPointType',
  full_name='appdynamics.pb.Agent.ExitPointType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='EXIT_HTTP', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EXIT_DB', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EXIT_CACHE', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EXIT_RABBITMQ', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EXIT_WEBSERVICE', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EXIT_CUSTOM', index=5, number=5,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=205,
  serialized_end=321,
)

ExitPointType = enum_type_wrapper.EnumTypeWrapper(_EXITPOINTTYPE)
PHP_WEB = 0
PHP_MVC = 1
PHP_DRUPAL = 2
PHP_WORDPRESS = 3
PHP_CLI = 4
PHP_WEB_SERVICE = 5
NODEJS_WEB = 6
NATIVE = 7
PYTHON_WEB = 8
WEB = 9
EXIT_HTTP = 0
EXIT_DB = 1
EXIT_CACHE = 2
EXIT_RABBITMQ = 3
EXIT_WEBSERVICE = 4
EXIT_CUSTOM = 5




DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), '\n\016appdynamics.pb')
# @@protoc_insertion_point(module_scope)
