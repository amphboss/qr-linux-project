import os
import pytest
import shutil
from shared.qr_generator import QRGenerator

TEST_OUTPUT_DIR = "test_generated_qr"


@pytest.fixture(autouse=True)
def cleanup():
    """Создаём и удаляем тестовую папку для каждого теста."""
    yield
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)


@pytest.fixture
def generator():
    return QRGenerator(output_dir=TEST_OUTPUT_DIR)


# ===== Успешная генерация =====

def test_generate_creates_file(generator):
    path = generator.generate("Hello")
    assert os.path.isfile(path)
    assert path.endswith(".png")


def test_generate_file_not_empty(generator):
    path = generator.generate("Test data")
    assert os.path.getsize(path) > 0


def test_generate_creates_output_dir(generator):
    assert os.path.isdir(TEST_OUTPUT_DIR)


def test_generate_with_url(generator):
    path = generator.generate("https://example.com")
    assert os.path.isfile(path)


def test_generate_with_cyrillic(generator):
    path = generator.generate("Привет мир")
    assert os.path.isfile(path)


# ===== Параметры цвета =====

def test_generate_custom_colors(generator):
    path = generator.generate("color test", fill_color="#ff0000", back_color="#00ff00")
    assert os.path.isfile(path)


# ===== Параметры размера =====

def test_generate_custom_box_size(generator):
    path = generator.generate("size test", box_size=20)
    assert os.path.isfile(path)


def test_generate_custom_border(generator):
    path = generator.generate("border test", border=10)
    assert os.path.isfile(path)


# ===== Уровни коррекции ошибок =====

@pytest.mark.parametrize("level", ["L", "M", "Q", "H"])
def test_generate_error_levels(generator, level):
    path = generator.generate(f"error level {level}", error=level)
    assert os.path.isfile(path)


def test_generate_unknown_error_level_falls_back(generator):
    path = generator.generate("fallback test", error="X")
    assert os.path.isfile(path)


# ===== Валидация =====

def test_generate_empty_string_raises(generator):
    with pytest.raises(ValueError):
        generator.generate("")


def test_generate_whitespace_only_raises(generator):
    with pytest.raises(ValueError):
        generator.generate("   ")


def test_generate_none_raises(generator):
    with pytest.raises(ValueError):
        generator.generate(None)


# ===== Уникальность файлов =====

def test_generate_unique_filenames(generator):
    import time
    path1 = generator.generate("unique1")
    time.sleep(1)
    path2 = generator.generate("unique2")
    assert path1 != path2
