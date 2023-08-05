# Copyright 2015 Sebastian Kreft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import collections
import os.path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image


def _images_are_equal(filename1, filename2):
    # We need to convert both images to the same format, as the resulting one
    # may have lost the alpha channel (alpha=255) or may be now indexed
    # (L or P mode).
    img1 = Image.open(filename1).convert('RGBA')
    img2 = Image.open(filename2).convert('RGBA')

    return img1.tobytes() == img2.tobytes()


# Magic numbers taken from https://en.wikipedia.org/wiki/List_of_file_signatures
_JPEG_MAGIC_NUMBER = b'\xFF\xD8\xFF'
_PNG_MAGIC_NUMBER = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'


def _check_magic_number(filename, magic_number):
    """Check whether the filename starts with the provided magic number."""
    with open(filename, 'rb') as f:
        return f.read(len(magic_number)) == magic_number


def _is_jpeg(filename):
    """Check whether the filename is a valid JPEG file."""
    return _check_magic_number(filename, _JPEG_MAGIC_NUMBER)


def _is_png(filename):
    """Check whether the filename is a valid PNG file."""
    return _check_magic_number(filename, _PNG_MAGIC_NUMBER)


def _get_temporary_filename(prefix='tmp'):
    temp_file = tempfile.NamedTemporaryFile(prefix=prefix)
    temp_name = temp_file.name
    temp_file.close()

    return temp_name


class InvalidExtension(Exception):
    """The file extension does not correspond to the file contents."""


class MissingBinary(FileNotFoundError):
    """The binary does not exist."""


def _call_binary(args):
    try:
        return subprocess.check_output(args, stderr=subprocess.STDOUT)
    except FileNotFoundError as error:
        raise MissingBinary(error.errno, 'binary not found', args[0])


def _pngcrush(input_filename, output_filename):
    _call_binary(['pngcrush', '-rem', 'alla', '-reduce', '-brute', '-q',
                  input_filename, output_filename])


def _optipng(input_filename, output_filename):
    _call_binary(['optipng', '-out', output_filename, '-o9', '-quiet',
                   input_filename])


def _jpegtran(input_filename, output_filename):
    _call_binary(['jpegtran', '-copy', 'none', '-optimize', '-perfect',
                  '-outfile', output_filename, input_filename])


def _jpegoptim(input_filename, output_filename):
    # jpegoptim replaces the input file with the compressed version, so we first
    # need to copy the input file to the output file.
    shutil.copy(input_filename, output_filename)
    _call_binary(['jpegoptim', '--strip-all', '--quiet', output_filename])


_CompressorResult = collections.namedtuple('_CompressorResult',
                                           ['size', 'filename'])


def _process(input_filename, compressor):
    """Helper function to compress an image.

    Returns:
      _CompressorResult named tuple, with the resulting size and the temporary
      filename used.
    """
    result_filename = _get_temporary_filename(prefix=compressor.__name__)
    compressor(input_filename, result_filename)
    result_size = os.path.getsize(result_filename)

    return _CompressorResult(result_size, result_filename)


def _compress_with(input_filename, output_filename, compressors):
    """Helper function to compress an image with several compressors.

    In case the compressors do not improve the filesize or in case the resulting
    image is not equivalent to the source, then the output will be a copy of the
    input.
    """
    results = [
        _process(input_filename, compressor) for compressor in compressors]
    best_result = min(results)
    os.rename(best_result.filename, output_filename)

    if (best_result.size >= os.path.getsize(input_filename) or
            not _images_are_equal(input_filename, output_filename)):
        shutil.copy(input_filename, output_filename)


def jpeg_compressor(input_filename, output_filename):
    """Loslessly recompress a JPEG.

    Raises:
      InvalidExtension in case the input is not a JPEG.
    """
    if not _is_jpeg(input_filename):
        raise InvalidExtension()

    _compress_with(input_filename, output_filename, [_jpegtran, _jpegoptim])


def png_compressor(input_filename, output_filename):
    """Loslessly recompress a JPEG.

    Raises:
      InvalidExtension in case the input is not a PNG.
    """
    if not _is_png(input_filename):
        raise InvalidExtension()

    _compress_with(input_filename, output_filename, [_pngcrush, _optipng])


_EXTENSION_MAPPING = {
    '.jpeg': jpeg_compressor,
    '.jpg': jpeg_compressor,
    '.png': png_compressor,
}


def _parse_argv(argv):
    parser = argparse.ArgumentParser(
        description='Losslessly compress JPEG and PNG files.')
    parser.add_argument(
        '--replace',
        action='store_true',
        help='replace the input file in case we can compress it')
    parser.add_argument('filename',
                        action='store',
                        help='the filename to compress')
    parser.add_argument('--output',
                        action='store',
                        help='the filename to compress',
                        required=False)
    args = parser.parse_args(argv)

    return args


def main(argv):
    args = _parse_argv(argv)
    filename = args.filename

    if not os.path.isfile(filename):
        sys.stderr.write(
            '{} is not an image file\n'.format(filename))
        return 3

    _, extension = os.path.splitext(filename)
    extension = extension.lower()
    compressor = _EXTENSION_MAPPING.get(extension)
    if compressor is None:
        sys.stderr.write(
            'No lossless compressor defined for extension "{}"\n'.format(
                extension))
        return 4

    output_filename = _get_temporary_filename(prefix='lossless-compressor')
    try:
        compressor(filename, output_filename)
    except InvalidExtension as error:
        sys.stderr.write(
            '{} is not a "{}" file. Please correct the extension\n'.format(
                filename, extension))
        return 5
    except MissingBinary as error:
        sys.stderr.write(
            'The executable "{}" was not found. '.format(error.filename) +
            'Please install it and re-run this command.\n')
        return 6
    except subprocess.CalledProcessError as error:
        sys.stderr.write(
            'Error when running the command:\n  ' +
            '{}\n'.format(' '.join(error.cmd)))
        sys.stderr.write('Status: {}\n'.format(error.returncode))
        sys.stderr.write('Output:\n')
        sys.stderr.write(error.output.decode('utf-8'))
        return 7

    original_size = os.path.getsize(filename)
    new_size = os.path.getsize(output_filename)
    reduction = original_size - new_size
    reduction_percentage = reduction * 100 / original_size
    savings = 'savings: {} bytes = {:.2f}%'.format(
        reduction, reduction_percentage)

    if new_size < original_size:
        if args.replace or args.output is not None:
            if args.replace:
                shutil.copy(output_filename, filename)
            else:
                shutil.copy(output_filename, args.output)

            print('File was losslessly compressed to {} bytes ({})'.format(
                new_size, savings))
            return 0
        else:
            print(
                'File can be losslessly compressed to {} bytes ({})'.format(
                    new_size, savings))
            print('Replace it by running either:')
            print('  optimage --replace {}'.format(filename))
            print('  optimage --output <FILENAME> {}'.format(filename))
            return 1

    return 0


__all__ = (jpeg_compressor, png_compressor)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
