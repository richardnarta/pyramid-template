from marshmallow import Schema, fields


class BaseSchema(Schema):
    error_messages = {
        "required": "Kolom ini harus diisi.",
        "unknown": "Kolom tidak dikenal.",
        "invalid": "Nilai tidak valid.",
        "type": "Tipe data tidak sesuai.",
        "null": "Kolom ini tidak boleh kosong.",
        "validator_failed": "Nilai tidak valid."
    }

    for key, value in error_messages.items():
        fields.Field.default_error_messages["key"] = value
