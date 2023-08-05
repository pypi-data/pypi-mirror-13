# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: authority_keys.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='authority_keys.proto',
  package='extensions.core_api.cast_channel.proto',
  syntax='proto2',
  serialized_pb=_b('\n\x14\x61uthority_keys.proto\x12&extensions.core_api.cast_channel.proto\"\x88\x01\n\rAuthorityKeys\x12G\n\x04keys\x18\x01 \x03(\x0b\x32\x39.extensions.core_api.cast_channel.proto.AuthorityKeys.Key\x1a.\n\x03Key\x12\x13\n\x0b\x66ingerprint\x18\x01 \x02(\x0c\x12\x12\n\npublic_key\x18\x02 \x02(\x0c\x42\x02H\x03')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_AUTHORITYKEYS_KEY = _descriptor.Descriptor(
  name='Key',
  full_name='extensions.core_api.cast_channel.proto.AuthorityKeys.Key',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='fingerprint', full_name='extensions.core_api.cast_channel.proto.AuthorityKeys.Key.fingerprint', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='public_key', full_name='extensions.core_api.cast_channel.proto.AuthorityKeys.Key.public_key', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=155,
  serialized_end=201,
)

_AUTHORITYKEYS = _descriptor.Descriptor(
  name='AuthorityKeys',
  full_name='extensions.core_api.cast_channel.proto.AuthorityKeys',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='keys', full_name='extensions.core_api.cast_channel.proto.AuthorityKeys.keys', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_AUTHORITYKEYS_KEY, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=65,
  serialized_end=201,
)

_AUTHORITYKEYS_KEY.containing_type = _AUTHORITYKEYS
_AUTHORITYKEYS.fields_by_name['keys'].message_type = _AUTHORITYKEYS_KEY
DESCRIPTOR.message_types_by_name['AuthorityKeys'] = _AUTHORITYKEYS

AuthorityKeys = _reflection.GeneratedProtocolMessageType('AuthorityKeys', (_message.Message,), dict(

  Key = _reflection.GeneratedProtocolMessageType('Key', (_message.Message,), dict(
    DESCRIPTOR = _AUTHORITYKEYS_KEY,
    __module__ = 'authority_keys_pb2'
    # @@protoc_insertion_point(class_scope:extensions.core_api.cast_channel.proto.AuthorityKeys.Key)
    ))
  ,
  DESCRIPTOR = _AUTHORITYKEYS,
  __module__ = 'authority_keys_pb2'
  # @@protoc_insertion_point(class_scope:extensions.core_api.cast_channel.proto.AuthorityKeys)
  ))
_sym_db.RegisterMessage(AuthorityKeys)
_sym_db.RegisterMessage(AuthorityKeys.Key)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('H\003'))
# @@protoc_insertion_point(module_scope)
