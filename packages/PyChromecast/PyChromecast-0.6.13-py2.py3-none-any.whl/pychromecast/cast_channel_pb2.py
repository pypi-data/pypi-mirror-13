# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cast_channel.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='cast_channel.proto',
  package='extensions.core_api.cast_channel',
  syntax='proto2',
  serialized_pb=_b('\n\x12\x63\x61st_channel.proto\x12 extensions.core_api.cast_channel\"\xed\x02\n\x0b\x43\x61stMessage\x12W\n\x10protocol_version\x18\x01 \x02(\x0e\x32=.extensions.core_api.cast_channel.CastMessage.ProtocolVersion\x12\x11\n\tsource_id\x18\x02 \x02(\t\x12\x16\n\x0e\x64\x65stination_id\x18\x03 \x02(\t\x12\x11\n\tnamespace\x18\x04 \x02(\t\x12O\n\x0cpayload_type\x18\x05 \x02(\x0e\x32\x39.extensions.core_api.cast_channel.CastMessage.PayloadType\x12\x14\n\x0cpayload_utf8\x18\x06 \x01(\t\x12\x16\n\x0epayload_binary\x18\x07 \x01(\x0c\"!\n\x0fProtocolVersion\x12\x0e\n\nCASTV2_1_0\x10\x00\"%\n\x0bPayloadType\x12\n\n\x06STRING\x10\x00\x12\n\n\x06\x42INARY\x10\x01\"s\n\rAuthChallenge\x12\x62\n\x13signature_algorithm\x18\x01 \x01(\x0e\x32\x34.extensions.core_api.cast_channel.SignatureAlgorithm:\x0fRSASSA_PKCS1v15\"\xc8\x01\n\x0c\x41uthResponse\x12\x11\n\tsignature\x18\x01 \x02(\x0c\x12\x1f\n\x17\x63lient_auth_certificate\x18\x02 \x02(\x0c\x12 \n\x18intermediate_certificate\x18\x03 \x03(\x0c\x12\x62\n\x13signature_algorithm\x18\x04 \x01(\x0e\x32\x34.extensions.core_api.cast_channel.SignatureAlgorithm:\x0fRSASSA_PKCS1v15\"\xa8\x01\n\tAuthError\x12I\n\nerror_type\x18\x01 \x02(\x0e\x32\x35.extensions.core_api.cast_channel.AuthError.ErrorType\"P\n\tErrorType\x12\x12\n\x0eINTERNAL_ERROR\x10\x00\x12\n\n\x06NO_TLS\x10\x01\x12#\n\x1fSIGNATURE_ALGORITHM_UNAVAILABLE\x10\x02\"\xd5\x01\n\x11\x44\x65viceAuthMessage\x12\x42\n\tchallenge\x18\x01 \x01(\x0b\x32/.extensions.core_api.cast_channel.AuthChallenge\x12@\n\x08response\x18\x02 \x01(\x0b\x32..extensions.core_api.cast_channel.AuthResponse\x12:\n\x05\x65rror\x18\x03 \x01(\x0b\x32+.extensions.core_api.cast_channel.AuthError*J\n\x12SignatureAlgorithm\x12\x0f\n\x0bUNSPECIFIED\x10\x00\x12\x13\n\x0fRSASSA_PKCS1v15\x10\x01\x12\x0e\n\nRSASSA_PSS\x10\x02\x42\x02H\x03')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_SIGNATUREALGORITHM = _descriptor.EnumDescriptor(
  name='SignatureAlgorithm',
  full_name='extensions.core_api.cast_channel.SignatureAlgorithm',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNSPECIFIED', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RSASSA_PKCS1v15', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RSASSA_PSS', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1131,
  serialized_end=1205,
)
_sym_db.RegisterEnumDescriptor(_SIGNATUREALGORITHM)

SignatureAlgorithm = enum_type_wrapper.EnumTypeWrapper(_SIGNATUREALGORITHM)
UNSPECIFIED = 0
RSASSA_PKCS1v15 = 1
RSASSA_PSS = 2


_CASTMESSAGE_PROTOCOLVERSION = _descriptor.EnumDescriptor(
  name='ProtocolVersion',
  full_name='extensions.core_api.cast_channel.CastMessage.ProtocolVersion',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='CASTV2_1_0', index=0, number=0,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=350,
  serialized_end=383,
)
_sym_db.RegisterEnumDescriptor(_CASTMESSAGE_PROTOCOLVERSION)

_CASTMESSAGE_PAYLOADTYPE = _descriptor.EnumDescriptor(
  name='PayloadType',
  full_name='extensions.core_api.cast_channel.CastMessage.PayloadType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STRING', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BINARY', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=385,
  serialized_end=422,
)
_sym_db.RegisterEnumDescriptor(_CASTMESSAGE_PAYLOADTYPE)

_AUTHERROR_ERRORTYPE = _descriptor.EnumDescriptor(
  name='ErrorType',
  full_name='extensions.core_api.cast_channel.AuthError.ErrorType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='INTERNAL_ERROR', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NO_TLS', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SIGNATURE_ALGORITHM_UNAVAILABLE', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=833,
  serialized_end=913,
)
_sym_db.RegisterEnumDescriptor(_AUTHERROR_ERRORTYPE)


_CASTMESSAGE = _descriptor.Descriptor(
  name='CastMessage',
  full_name='extensions.core_api.cast_channel.CastMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='protocol_version', full_name='extensions.core_api.cast_channel.CastMessage.protocol_version', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='source_id', full_name='extensions.core_api.cast_channel.CastMessage.source_id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='destination_id', full_name='extensions.core_api.cast_channel.CastMessage.destination_id', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='namespace', full_name='extensions.core_api.cast_channel.CastMessage.namespace', index=3,
      number=4, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='payload_type', full_name='extensions.core_api.cast_channel.CastMessage.payload_type', index=4,
      number=5, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='payload_utf8', full_name='extensions.core_api.cast_channel.CastMessage.payload_utf8', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='payload_binary', full_name='extensions.core_api.cast_channel.CastMessage.payload_binary', index=6,
      number=7, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CASTMESSAGE_PROTOCOLVERSION,
    _CASTMESSAGE_PAYLOADTYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=57,
  serialized_end=422,
)


_AUTHCHALLENGE = _descriptor.Descriptor(
  name='AuthChallenge',
  full_name='extensions.core_api.cast_channel.AuthChallenge',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='signature_algorithm', full_name='extensions.core_api.cast_channel.AuthChallenge.signature_algorithm', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=1,
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
  serialized_start=424,
  serialized_end=539,
)


_AUTHRESPONSE = _descriptor.Descriptor(
  name='AuthResponse',
  full_name='extensions.core_api.cast_channel.AuthResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='signature', full_name='extensions.core_api.cast_channel.AuthResponse.signature', index=0,
      number=1, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='client_auth_certificate', full_name='extensions.core_api.cast_channel.AuthResponse.client_auth_certificate', index=1,
      number=2, type=12, cpp_type=9, label=2,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='intermediate_certificate', full_name='extensions.core_api.cast_channel.AuthResponse.intermediate_certificate', index=2,
      number=3, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='signature_algorithm', full_name='extensions.core_api.cast_channel.AuthResponse.signature_algorithm', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=1,
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
  serialized_start=542,
  serialized_end=742,
)


_AUTHERROR = _descriptor.Descriptor(
  name='AuthError',
  full_name='extensions.core_api.cast_channel.AuthError',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='error_type', full_name='extensions.core_api.cast_channel.AuthError.error_type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _AUTHERROR_ERRORTYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=745,
  serialized_end=913,
)


_DEVICEAUTHMESSAGE = _descriptor.Descriptor(
  name='DeviceAuthMessage',
  full_name='extensions.core_api.cast_channel.DeviceAuthMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='challenge', full_name='extensions.core_api.cast_channel.DeviceAuthMessage.challenge', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='response', full_name='extensions.core_api.cast_channel.DeviceAuthMessage.response', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='error', full_name='extensions.core_api.cast_channel.DeviceAuthMessage.error', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=916,
  serialized_end=1129,
)

_CASTMESSAGE.fields_by_name['protocol_version'].enum_type = _CASTMESSAGE_PROTOCOLVERSION
_CASTMESSAGE.fields_by_name['payload_type'].enum_type = _CASTMESSAGE_PAYLOADTYPE
_CASTMESSAGE_PROTOCOLVERSION.containing_type = _CASTMESSAGE
_CASTMESSAGE_PAYLOADTYPE.containing_type = _CASTMESSAGE
_AUTHCHALLENGE.fields_by_name['signature_algorithm'].enum_type = _SIGNATUREALGORITHM
_AUTHRESPONSE.fields_by_name['signature_algorithm'].enum_type = _SIGNATUREALGORITHM
_AUTHERROR.fields_by_name['error_type'].enum_type = _AUTHERROR_ERRORTYPE
_AUTHERROR_ERRORTYPE.containing_type = _AUTHERROR
_DEVICEAUTHMESSAGE.fields_by_name['challenge'].message_type = _AUTHCHALLENGE
_DEVICEAUTHMESSAGE.fields_by_name['response'].message_type = _AUTHRESPONSE
_DEVICEAUTHMESSAGE.fields_by_name['error'].message_type = _AUTHERROR
DESCRIPTOR.message_types_by_name['CastMessage'] = _CASTMESSAGE
DESCRIPTOR.message_types_by_name['AuthChallenge'] = _AUTHCHALLENGE
DESCRIPTOR.message_types_by_name['AuthResponse'] = _AUTHRESPONSE
DESCRIPTOR.message_types_by_name['AuthError'] = _AUTHERROR
DESCRIPTOR.message_types_by_name['DeviceAuthMessage'] = _DEVICEAUTHMESSAGE
DESCRIPTOR.enum_types_by_name['SignatureAlgorithm'] = _SIGNATUREALGORITHM

CastMessage = _reflection.GeneratedProtocolMessageType('CastMessage', (_message.Message,), dict(
  DESCRIPTOR = _CASTMESSAGE,
  __module__ = 'cast_channel_pb2'
  # @@protoc_insertion_point(class_scope:extensions.core_api.cast_channel.CastMessage)
  ))
_sym_db.RegisterMessage(CastMessage)

AuthChallenge = _reflection.GeneratedProtocolMessageType('AuthChallenge', (_message.Message,), dict(
  DESCRIPTOR = _AUTHCHALLENGE,
  __module__ = 'cast_channel_pb2'
  # @@protoc_insertion_point(class_scope:extensions.core_api.cast_channel.AuthChallenge)
  ))
_sym_db.RegisterMessage(AuthChallenge)

AuthResponse = _reflection.GeneratedProtocolMessageType('AuthResponse', (_message.Message,), dict(
  DESCRIPTOR = _AUTHRESPONSE,
  __module__ = 'cast_channel_pb2'
  # @@protoc_insertion_point(class_scope:extensions.core_api.cast_channel.AuthResponse)
  ))
_sym_db.RegisterMessage(AuthResponse)

AuthError = _reflection.GeneratedProtocolMessageType('AuthError', (_message.Message,), dict(
  DESCRIPTOR = _AUTHERROR,
  __module__ = 'cast_channel_pb2'
  # @@protoc_insertion_point(class_scope:extensions.core_api.cast_channel.AuthError)
  ))
_sym_db.RegisterMessage(AuthError)

DeviceAuthMessage = _reflection.GeneratedProtocolMessageType('DeviceAuthMessage', (_message.Message,), dict(
  DESCRIPTOR = _DEVICEAUTHMESSAGE,
  __module__ = 'cast_channel_pb2'
  # @@protoc_insertion_point(class_scope:extensions.core_api.cast_channel.DeviceAuthMessage)
  ))
_sym_db.RegisterMessage(DeviceAuthMessage)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('H\003'))
# @@protoc_insertion_point(module_scope)
