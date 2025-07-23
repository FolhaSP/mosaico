import base64

import pytest
from pydantic import ValidationError

from mosaico.integrations.base.adapters import Adapter
from mosaico.media import Media


def create_temp_file(tmp_path, content, filename):
    file_path = tmp_path / filename
    file_path.write_text(content)
    return file_path


def test_creation():
    media = Media(data="test content")
    assert media.data == "test content"
    assert media.path is None
    assert media.mime_type is None
    assert media.metadata == {}


def test_creation_with_path():
    media = Media(path="/path/to/file.txt")
    assert media.data is None
    assert media.path == "/path/to/file.txt"
    assert media.mime_type is None
    assert media.metadata == {}


def test_decode_base64_str_to_bytes():
    original = b"hello world \xf0\x9f\x8c\x8d"
    b64 = base64.b64encode(original).decode("ascii")
    m = Media(data=b64, path=None)
    assert isinstance(m.data, bytes)
    assert m.data == original


def test_encode_bytes_to_base64_json():
    original = b"foo bar baz"
    m = Media(data=original, path=None)
    m_dict = m.model_dump(mode="json")
    assert isinstance(m_dict["data"], str)
    decoded = base64.b64decode(m_dict["data"])
    assert decoded == original


def test_round_trip_via_model_dump_and_parse():
    original = b"\x00\x01\x02binary\xff"
    b64 = base64.b64encode(original).decode("ascii")
    m1 = Media.from_data(b64)
    json_str = m1.model_dump_json()
    m2 = Media.model_validate_json(json_str)
    assert isinstance(m2.data, bytes)
    assert m2.data == original


def test_non_base64_string_pass_through():
    raw = "not base64!!!"
    m = Media(data=raw)
    assert isinstance(m.data, str)
    assert m.data == raw


def test_non_ascii_string_pass_through():
    raw = "hello 😊"
    m = Media(data=raw)
    assert isinstance(m.data, str)
    assert m.data == raw


def test_length_not_multiple_of_four_pass_through():
    raw = "YWxsb3c"
    assert len(raw) % 4 != 0
    m = Media(data=raw)
    assert isinstance(m.data, str)
    assert m.data == raw


def test_empty_string_pass_through():
    raw = ""
    m = Media(data=raw)
    assert isinstance(m.data, str)
    assert m.data == raw


def test_bytes_input_unchanged():
    original = b"abcd"
    m = Media(data=original)
    assert isinstance(m.data, bytes)
    assert m.data == original


def test_creation_with_mime_type():
    media = Media(data="test content", mime_type="text/plain")
    assert media.data == "test content"
    assert media.mime_type == "text/plain"


def test_creation_with_metadata():
    metadata = {"author": "John Doe", "date": "2023-04-01"}
    media = Media(data="test content", metadata=metadata)
    assert media.metadata == metadata


def test_validate_media_with_data():
    media = Media(data="test content")
    assert media.data == "test content"
    assert media.path is None


def test_validate_media_with_path():
    media = Media(path="/path/to/file.txt")
    assert media.data is None
    assert media.path == "/path/to/file.txt"


def test_validate_media_without_data_or_path():
    with pytest.raises(ValidationError, match="Either data or path must be provided"):
        Media()


def test_from_path(tmp_path):
    file_path = create_temp_file(tmp_path, "test", "test.txt")
    media = Media.from_path(file_path)
    assert media.data is None
    assert media.path == file_path
    assert media.mime_type == "text/plain"


def test_from_path_with_encoding(tmp_path):
    file_path = create_temp_file(tmp_path, "test", "test.txt")
    media = Media.from_path(file_path, encoding="ascii")
    assert media.data is None
    assert media.path == file_path
    assert media.encoding == "ascii"


def test_from_path_with_custom_mime_type(tmp_path):
    file_path = create_temp_file(tmp_path, "test content", "test.txt")
    media = Media.from_path(file_path, mime_type="application/custom")
    assert media.mime_type == "application/custom"


def test_from_path_no_guess_mime_type(tmp_path):
    file_path = create_temp_file(tmp_path, "test content", "test.txt")
    media = Media.from_path(file_path, guess_mime_type=False)
    assert media.mime_type is None


def test_from_path_with_metadata(tmp_path):
    file_path = create_temp_file(tmp_path, "test content", "test.txt")
    metadata = {"author": "John Doe"}
    media = Media.from_path(file_path, metadata=metadata)
    assert media.metadata == metadata


def test_from_data_str():
    media = Media.from_data("test content")
    assert media.data == "test content"


def test_from_data_bytes():
    media = Media.from_data(b"test content")
    assert media.data == b"test content"


def test_from_data_with_path():
    media = Media.from_data("test content", path="/path/to/file.txt")
    assert media.data == "test content"
    assert media.path == "/path/to/file.txt"


def test_from_data_with_mime_type():
    media = Media.from_data("test content", mime_type="text/plain")
    assert media.mime_type == "text/plain"


def test_from_data_with_metadata():
    metadata = {"author": "John Doe"}
    media = Media.from_data("test content", metadata=metadata)
    assert media.metadata == metadata


def test_to_string_with_str_data():
    media = Media(data="test content")
    assert media.to_string() == "test content"


def test_to_string_with_bytes_data():
    media = Media(data=b"test content")
    assert media.to_string() == "test content"


def test_to_string_with_file_path(tmp_path):
    file_path = create_temp_file(tmp_path, "test content", "test.txt")
    media = Media(path=file_path)
    assert media.to_string() == "test content"


def test_to_string_with_non_utf8_encoding(tmp_path):
    file_path = create_temp_file(tmp_path, "test content", "test.txt")
    media = Media(path=file_path, encoding="ascii")
    assert media.to_string() == "test content"


def test_to_bytes_with_bytes_data():
    media = Media(data=b"test content")
    assert media.to_bytes() == b"test content"


def test_to_bytes_with_str_data():
    media = Media(data="test content")
    assert media.to_bytes() == b"test content"


def test_to_bytes_with_file_path(tmp_path):
    file_path = create_temp_file(tmp_path, "test content", "test.txt")
    media = Media(path=file_path)
    assert media.to_bytes() == b"test content"


def test_to_bytes_with_non_utf8_encoding(tmp_path):
    file_path = create_temp_file(tmp_path, "test content", "test.txt")
    media = Media(path=file_path, encoding="ascii")
    assert media.to_bytes() == b"test content"


def test_to_bytes_io_with_bytes_data():
    media = Media(data=b"test content")
    with media.to_bytes_io() as byte_stream:
        assert byte_stream.read() == b"test content"


def test_to_bytes_io_with_file_path(tmp_path):
    file_path = create_temp_file(tmp_path, "test content", "test.txt")
    media = Media(path=file_path)
    with media.to_bytes_io() as byte_stream:
        assert byte_stream.read() == b"test content"


class MockMediaAdapter(Adapter[Media, dict]):
    """Mock adapter for testing purposes"""

    def to_external(self, obj: Media) -> dict:
        """Convert Media to a dictionary representation"""
        return {
            "id": obj.id,
            "data": obj.data,
            "path": str(obj.path) if obj.path else None,
            "mime_type": obj.mime_type,
            "encoding": obj.encoding,
            "metadata": obj.metadata,
        }

    def from_external(self, external: dict) -> Media:
        """Convert dictionary representation to Media"""
        return Media(
            id=external["id"],
            data=external["data"],
            path=external["path"],
            mime_type=external["mime_type"],
            encoding=external["encoding"],
            metadata=external["metadata"],
        )


def test_media_from_external():
    """Test Media.from_external method"""
    adapter = MockMediaAdapter()
    external_data = {
        "id": "test-id",
        "data": "test data",
        "path": None,
        "mime_type": "text/plain",
        "encoding": "utf-8",
        "metadata": {"description": "Test description"},
    }

    media = Media.from_external(adapter, external_data)

    assert isinstance(media, Media)
    assert media.id == "test-id"
    assert media.data == "test data"
    assert media.path is None
    assert media.mime_type == "text/plain"
    assert media.encoding == "utf-8"
    assert media.metadata == {"description": "Test description"}


def test_media_to_external():
    """Test Media.to_external method"""
    adapter = MockMediaAdapter()
    media = Media(id="test-id", data="test data", mime_type="text/plain", metadata={"credit": "Test credit"})

    external = media.to_external(adapter)

    assert isinstance(external, dict)
    assert external["id"] == "test-id"
    assert external["data"] == "test data"
    assert external["mime_type"] == "text/plain"
    assert external["metadata"] == {"credit": "Test credit"}


def test_media_roundtrip_conversion():
    """Test round-trip conversion from Media to external and back"""
    adapter = MockMediaAdapter()
    original_media = Media(
        id="test-id", data="test data", mime_type="text/plain", metadata={"description": "Test description"}
    )

    external = original_media.to_external(adapter)
    converted_media = Media.from_external(adapter, external)

    assert original_media.id == converted_media.id
    assert original_media.data == converted_media.data
    assert original_media.mime_type == converted_media.mime_type
    assert original_media.metadata == converted_media.metadata


def test_metadata_properties_extraction():
    """Test extraction of credits metadata"""
    media = Media(
        id="test-id",
        data="test data",
        mime_type="text/plain",
        metadata={"description": "Test description", "credits": ["Credit 1", "Credit 2"]},
    )
    media_credits = media.credits
    description = media.description
    assert description == "Test description"
    assert media_credits == ["Credit 1", "Credit 2"]


def test_base64_minimum_length_requirement():
    """Test that short strings are not treated as base64"""
    # Short strings that look like base64 but are too short (less than 16 chars)
    short_strings = [
        "YWxsb3c",  # 7 chars
        "aGVsbG8",  # 7 chars
        "dGVzdA==",  # 8 chars
        "SGVsbG8gV29ybGQ",  # 15 chars
    ]

    for short_str in short_strings:
        media = Media(data=short_str)
        assert isinstance(media.data, str)
        assert media.data == short_str


def test_base64_without_padding():
    """Test base64 decoding without padding"""
    # Create base64 data without padding
    original = b"hello world test"
    b64_with_padding = base64.b64encode(original).decode("ascii")
    # Remove padding
    b64_without_padding = b64_with_padding.rstrip("=")

    # Should still decode correctly
    media = Media(data=b64_without_padding)
    assert isinstance(media.data, bytes)
    assert media.data == original


def test_base64_with_padding_still_works():
    """Test that base64 with padding still works as before"""
    original = b"hello world test data"
    b64_with_padding = base64.b64encode(original).decode("ascii")

    media = Media(data=b64_with_padding)
    assert isinstance(media.data, bytes)
    assert media.data == original


def test_base64_detection_edge_cases():
    """Test various edge cases for base64 detection"""
    # Valid base64 that meets minimum length
    valid_b64 = base64.b64encode(b"this is a test string").decode("ascii")
    media = Media(data=valid_b64)
    assert isinstance(media.data, bytes)

    # Invalid base64 characters but meets length requirement
    invalid_b64 = "InvalidBase64@#$%"
    media = Media(data=invalid_b64)
    assert isinstance(media.data, str)
    assert media.data == invalid_b64

    # Non-base64 string that meets length requirement
    long_text = "this is just a regular long text string"
    media = Media(data=long_text)
    assert isinstance(media.data, str)
    assert media.data == long_text


def test_to_bytes_io_with_string_data():
    """Test to_bytes_io method with string data"""
    test_string = "hello world test"
    media = Media(data=test_string)

    with media.to_bytes_io() as byte_stream:
        result = byte_stream.read()
        assert result == test_string.encode("utf-8")


def test_to_bytes_io_with_string_data_custom_encoding():
    """Test to_bytes_io method with string data and custom encoding"""
    test_string = "hello world test"
    media = Media(data=test_string, encoding="ascii")

    with media.to_bytes_io() as byte_stream:
        result = byte_stream.read()
        assert result == test_string.encode("ascii")


def test_to_bytes_io_with_unicode_string():
    """Test to_bytes_io method with unicode string data"""
    test_string = "hello world 🌍 test"
    media = Media(data=test_string)

    with media.to_bytes_io() as byte_stream:
        result = byte_stream.read()
        assert result == test_string.encode("utf-8")


def test_base64_detection_with_non_ascii_characters():
    """Test that strings with non-ASCII characters are not decoded as base64"""
    test_string = "hello 🌍 world"
    media = Media(data=test_string)
    assert isinstance(media.data, str)
    assert media.data == test_string


def test_base64_detection_preserves_original_behavior():
    """Test that existing base64 detection behavior is preserved"""
    # Test cases that should still work as before
    test_cases = [
        # Valid base64 with padding
        (b"hello world", True),
        # Valid base64 without padding (new functionality)
        (b"hello world test", True),
        # Invalid base64 due to bad characters
        ("invalid@#$%", False),
        # Too short to be considered base64
        ("short", False),
        # Non-ASCII characters
        ("hello 🌍", False),
        # Empty string
        ("", False),
    ]

    for test_data, should_decode in test_cases:
        if isinstance(test_data, bytes):
            # Create base64 string
            b64_str = base64.b64encode(test_data).decode("ascii")
            if not should_decode:
                # Make it too short
                b64_str = b64_str[:10]
        else:
            b64_str = test_data

        media = Media(data=b64_str)

        if should_decode and isinstance(test_data, bytes):
            assert isinstance(media.data, bytes)
            assert media.data == test_data
        else:
            assert isinstance(media.data, str)
            assert media.data == b64_str
