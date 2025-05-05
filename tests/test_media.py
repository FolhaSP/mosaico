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
