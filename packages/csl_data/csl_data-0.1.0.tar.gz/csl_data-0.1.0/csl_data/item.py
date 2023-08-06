from csl_data.schema import _CslDataSchema, _LooseCslDataSchema
from csl_data._fragments import Item


class CslDataItem(_CslDataSchema, Item):

    document_schema = _CslDataSchema.document_schema['items']


class LooseCslDataItem(_LooseCslDataSchema, CslDataItem, Item):

    document_schema = _LooseCslDataSchema.document_schema['items']
