# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Common.proto

from appdynamics_bindeps.google.protobuf import descriptor as _descriptor
from appdynamics_bindeps.google.protobuf import message as _message
from appdynamics_bindeps.google.protobuf import reflection as _reflection
from appdynamics_bindeps.google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='Common.proto',
  package='appdynamics.pb.Common',
  serialized_pb='\n\x0c\x43ommon.proto\x12\x15\x61ppdynamics.pb.Common\"\xf2\x01\n\x14StringMatchCondition\x12>\n\x04type\x18\x01 \x02(\x0e\x32\x30.appdynamics.pb.Common.StringMatchCondition.Type\x12\x14\n\x0cmatchStrings\x18\x02 \x03(\t\x12\r\n\x05isNot\x18\x03 \x01(\x08\"u\n\x04Type\x12\n\n\x06\x45QUALS\x10\x00\x12\x0f\n\x0bSTARTS_WITH\x10\x01\x12\r\n\tENDS_WITH\x10\x02\x12\x0c\n\x08\x43ONTAINS\x10\x03\x12\x11\n\rMATCHES_REGEX\x10\x04\x12\x0e\n\nIS_IN_LIST\x10\x05\x12\x10\n\x0cIS_NOT_EMPTY\x10\x06\",\n\rNameValuePair\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\tB\x10\n\x0e\x61ppdynamics.pb')



_STRINGMATCHCONDITION_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='appdynamics.pb.Common.StringMatchCondition.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='EQUALS', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STARTS_WITH', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENDS_WITH', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CONTAINS', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MATCHES_REGEX', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IS_IN_LIST', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IS_NOT_EMPTY', index=6, number=6,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=165,
  serialized_end=282,
)


_STRINGMATCHCONDITION = _descriptor.Descriptor(
  name='StringMatchCondition',
  full_name='appdynamics.pb.Common.StringMatchCondition',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='appdynamics.pb.Common.StringMatchCondition.type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='matchStrings', full_name='appdynamics.pb.Common.StringMatchCondition.matchStrings', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='isNot', full_name='appdynamics.pb.Common.StringMatchCondition.isNot', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _STRINGMATCHCONDITION_TYPE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=40,
  serialized_end=282,
)


_NAMEVALUEPAIR = _descriptor.Descriptor(
  name='NameValuePair',
  full_name='appdynamics.pb.Common.NameValuePair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='appdynamics.pb.Common.NameValuePair.name', index=0,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='appdynamics.pb.Common.NameValuePair.value', index=1,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=284,
  serialized_end=328,
)

_STRINGMATCHCONDITION.fields_by_name['type'].enum_type = _STRINGMATCHCONDITION_TYPE
_STRINGMATCHCONDITION_TYPE.containing_type = _STRINGMATCHCONDITION;
DESCRIPTOR.message_types_by_name['StringMatchCondition'] = _STRINGMATCHCONDITION
DESCRIPTOR.message_types_by_name['NameValuePair'] = _NAMEVALUEPAIR

class StringMatchCondition(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _STRINGMATCHCONDITION

  # @@protoc_insertion_point(class_scope:appdynamics.pb.Common.StringMatchCondition)

class NameValuePair(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _NAMEVALUEPAIR

  # @@protoc_insertion_point(class_scope:appdynamics.pb.Common.NameValuePair)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), '\n\016appdynamics.pb')
# @@protoc_insertion_point(module_scope)
