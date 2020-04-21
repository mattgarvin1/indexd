POST_RECORD_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "additionalProperties": False,
    "description": "Create a new index from hash & size",
    "required": ["size", "hashes", "urls", "form"],
    "properties": {
        "baseid": {
            "type": "string",
            "pattern": "^.*[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
        },
        "form": {"enum": ["object", "container", "multipart"]},
        "size": {
            "description": "Size of the data being indexed in bytes",
            "type": "integer",
            "minimum": 0,
        },
        "file_name": {
            "description": "optional file name of the object",
            "type": "string",
        },
        "metadata": {
            "description": "optional metadata of the object",
            "type": "object",
        },
        "urls_metadata": {
            "description": "optional urls metadata of the object",
            "type": "object",
        },
        "version": {
            "description": "optional version string of the object",
            "type": "string",
        },
        "uploader": {
            "description": "optional uploader of the object",
            "type": "string",
        },
        "urls": {"type": "array", "items": {"type": "string"}},
        "acl": {"type": "array", "items": {"type": "string"}},
        "authz": {
            "description": "optional authorization rules of the object",
            "type": "array",
            "items": {"type": "string"},
        },
        "did": {
            "type": "string",
            "pattern": "^.*[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
        },
        "hashes": {
            "type": "object",
            "properties": {
                "md5": {"type": "string", "pattern": "^[0-9a-f]{32}$"},
                "sha1": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "sha512": {"type": "string", "pattern": "^[0-9a-f]{128}$"},
                "crc": {"type": "string", "pattern": "^[0-9a-f]{8}$"},
                "etag": {"type": "string", "pattern": "^[0-9a-f]{32}(-\d+)?$"},
            },
            "anyOf": [
                {"required": ["md5"]},
                {"required": ["sha1"]},
                {"required": ["sha256"]},
                {"required": ["sha512"]},
                {"required": ["crc"]},
                {"required": ["etag"]},
            ],
        },
    },
}

PUT_RECORD_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "additionalProperties": False,
    "description": "Update an index",
    "properties": {
        "urls": {"type": "array", "items": {"type": "string"}},
        "acl": {"type": "array", "items": {"type": "string"}},
        "authz": {"type": "array", "items": {"type": "string"}},
        "file_name": {"type": ["string", "null"]},
        "version": {"type": ["string", "null"]},
        "uploader": {"type": ["string", "null"]},
        "metadata": {"type": "object"},
        "urls_metadata": {"type": "object"},
    },
}

RECORD_ALIAS_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "additionalProperties": False,
    "description": "Aliases that can be used in place of an Index record's DID",
    "properties": {
        "aliases": {
            "type": "array",
            "items": {"type": "object", "properties": {"value": {"type": "string"}}},
        }
    },
}

BUNDLE_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "additionalProperties": False,
    "description": "Creates a new bundle",
    "required": ["bundles", "name"],
    "properties": {
        "bundle_id": {
            "type": "string",
            "pattern": "^.*[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
        },
        "name": {
            "description": "Required bundle name created my author of the bundle",
            "type": "string",
        },
        "bundles": {"description": "Expanded bundles and objects.", "type": "array",},
    },
}
