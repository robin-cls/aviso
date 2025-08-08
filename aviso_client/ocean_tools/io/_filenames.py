from __future__ import annotations

import abc
import collections.abc
import dataclasses as dc
import datetime as dt
import os
import re
import string
import typing as tp
from enum import Enum, auto

import numpy as np
import pandas as pda

from aviso_client.ocean_tools.time import (
    Period,
    fractional_julian_day_to_numpy,
    julian_day_to_numpy,
    numpy_to_fractional_julian_day,
    numpy_to_julian_day,
)

T = tp.TypeVar('T')

    
class ILayout(abc.ABC):
    @abc.abstractmethod
    def build_path(self, **filters):
        pass

    @abc.abstractmethod
    def validate_path(self, path:str, filters: dict):
        pass
    
class IWalkable(abc.ABC):
    def __init__(self, layout: ILayout):
        self.layout = layout

    @abc.abstractmethod
    def walk(self):
        """
        Walk the structure using provided filters.
        """
        pass
    
class FileNameField(abc.ABC, tp.Generic[T]):

    def __init__(self,
                 name: str,
                 default: T | None = None,
                 description: str = ''):
        self.name = name
        self.default = default
        self.field_description = description

    @property
    def description(self) -> str:
        return self.field_description + ' ' + self.test_description

    @abc.abstractmethod
    def decode(self, input_string: str) -> T:
        pass

    @abc.abstractmethod
    def encode(self, data: T) -> str:
        pass

    @property
    @abc.abstractmethod
    def test_description(self) -> str:
        pass

    def test(self, reference: T, tested: T) -> bool:
        return reference == tested

    @property
    @abc.abstractmethod
    def type(self) -> type[T]:
        return T


class FileNameFieldString(FileNameField):

    def decode(self, input_string: str) -> str:
        return input_string

    def encode(self, data: str) -> str:
        return data

    @property
    def test_description(self) -> str:
        return (
            'As a String field, it can filtered by giving a reference '
            'string. The tested value from the file name will be filtered out if it'
            ' is not equal to the reference value.')

    @property
    def type(self) -> type[str]:
        return str


class FileNameFieldDatetime(FileNameField):
    """Numpy datetime value.

    Attributes
    ----------
    name: str
        name of the field
    date_fmt: str|List
        date format
    """

    def __init__(self,
                 name: str,
                 date_fmt: str | list,
                 default: np.timedelta64 | None = None,
                 description: str = ''):
        super().__init__(name, default, description)
        if isinstance(date_fmt, str): date_fmt = [date_fmt]
        self.date_fmt = date_fmt

    def decode(self, input_string: str) -> np.datetime64:
        output_date = None
        for d_fmt in self.date_fmt:
            try:
                output_date = np.datetime64(
                    dt.datetime.strptime(input_string, d_fmt))
                break
            except ValueError:
                continue

        if not output_date:
            # In case the date conversion failed. This should not happen if
            # the input regex is properly configured (with groups defined with
            # \d)
            raise FileParsingError(
                f"Date '{input_string}' extracted from filename (group "
                f"'{self.name}') could not be converted to a numpy datetime.")

        return output_date

    def encode(self, data: np.datetime64) -> str:
        # dt.datetime does not handle nanosecond precision, so we must convert
        # the numpy timestamp before using dt.datetime to encode the date with
        # the given format
        return data.astype('M8[us]').astype(dt.datetime).strftime(
            self.date_fmt[0])

    @property
    def test_description(self) -> str:
        return (
            'As a DateTime field, it can be filtered by giving a reference '
            'Period, datetime. The tested value from the file name will be '
            'filtered out if it is not included or not equal to the reference '
            'Period or datetime respectively. The reference value can be given '
            f'as a string or tuple of string following the {self.date_fmt} '
            'formatting')

    def test(self, reference: Period | np.datetime64,
             tested: np.datetime64) -> bool:
        if isinstance(reference, Period):
            return reference.intersects(tested)
        else:
            return reference == tested

    @property
    def type(self) -> type[np.datetime64]:
        return np.datetime64


class FileNameFieldDateDelta(FileNameFieldDatetime):
    """Numpy datetime value.

    Attributes
    ----------
    name: str
        name of the field
    date_fmt: str
        date format
    delta: np.timedelta64
        time delta
    include_stop: bool
        Whether the delta is included or not, default to False
    """

    def __init__(self,
                 name: str,
                 date_fmt: str | list,
                 delta: np.timedelta64,
                 include_stop: bool = False,
                 default: Period | None = None,
                 description: str = ''):
        super().__init__(name, date_fmt, default, description)
        self.delta = delta
        self.include_stop = include_stop

    def decode(self, input_string: str) -> Period:
        output_date = super().decode(input_string)
        return Period(output_date,
                      output_date + self.delta,
                      include_stop=self.include_stop)

    def encode(self, data: Period) -> str:
        return super().encode(data.start)

    def test(self, reference: Period | np.datetime64, tested: Period) -> bool:
        return tested.intersects(reference)

    @property
    def test_description(self) -> str:
        return (
            'As a Period field, it can be filtered by giving a reference '
            'Period or datetime. The tested value from the file name will be '
            'filtered out if it does not intersect the reference Period or does'
            ' not contain the reference datetime. The reference value can be '
            'given as a string or tuple of string following the '
            f'{self.date_fmt} formatting')

    @property
    def type(self) -> type[Period]:
        return Period


class JulianDayCodec:

    FORMATS = ['days', 'days_hours', 'fractional']

    def __init__(self, julian_day_format: str, reference: np.datetime64):
        if julian_day_format not in self.FORMATS:
            msg = f'Unknown julian day format {julian_day_format}, acceptable options are {self.FORMATS}'
            raise ValueError(msg)
        self.format = julian_day_format
        self.reference = reference

    def decode(self, input_string: str) -> np.datetime64:
        try:
            if self.format == 'days_hours':
                split = input_string.split('_')
                output_date = julian_day_to_numpy(
                    (int(split[0]), int(split[1]), 0),
                    reference=self.reference)
            elif self.format == 'days':
                output_date = julian_day_to_numpy((int(input_string), 0, 0),
                                                  reference=self.reference)
            else:
                output_date = fractional_julian_day_to_numpy(
                    float(input_string), reference=self.reference)
            return output_date
        except (ValueError, IndexError) as e:
            raise FileParsingError(
                f'{input_string} is not a julian day matching format "{self.format}"'
            ) from e

    def encode(self, data: np.datetime64) -> str:
        # Convert the start. Much like the decoding, the delta is a given
        # variable and should not be part of the encoded string
        if self.format == 'days_hours':
            days, hours, _ = numpy_to_julian_day(data,
                                                 reference=self.reference)
            return f'{days:0>5d}_{hours:0>2d}'
        elif self.format == 'days':
            days, _, _ = numpy_to_julian_day(data, reference=self.reference)
            return f'{days:0>2d}'
        else:
            fractional_days = numpy_to_fractional_julian_day(
                data, reference=self.reference)
            return str(fractional_days)


class FileNameFieldDateJulianDelta(JulianDayCodec, FileNameField):
    """Datetime value given as a julian day.

    Attributes
    ----------
    name: str
        name of the field
    delta: np.timedelta64
        time delta
    reference
        Reference date for the given julian days
    include_stop: bool
        Whether the delta is included or not, default to False
    julian_day_format
        Whether the julian day is expected as 'days', 'days_hours' or
        'fractional'. For example 24000, 24000_06 or 24000.25
    """

    def __init__(
        self,
        name: str,
        delta: np.timedelta64,
        reference: np.datetime64,
        include_stop: bool = False,
        default: Period | None = None,
        description: str = '',
        julian_day_format: str = 'days',
    ):
        super().__init__(julian_day_format, reference)
        super(JulianDayCodec, self).__init__(name, default, description)
        self.delta = delta
        self.include_stop = include_stop

    def decode(self, input_string: str) -> Period:
        output_date = super().decode(input_string)
        return Period(output_date,
                      output_date + self.delta,
                      include_stop=self.include_stop)

    def encode(self, data: Period) -> str:
        return super().encode(data.start)

    @property
    def test_description(self) -> str:
        return (
            'As a Period field, it can be filtered by giving a reference '
            'Period or datetime. The tested value from the file name will be '
            'filtered out if it does not intersect the reference Period or contain '
            ' the reference datetime.')

    def test(self, reference: Period | np.datetime64, tested: Period) -> bool:
        return tested.intersects(reference)

    @property
    def type(self) -> type[Period]:
        return Period


class FileNameFieldDateJulian(JulianDayCodec, FileNameField):

    def __init__(self,
                 name: str,
                 reference: np.datetime64,
                 default: Period | None = None,
                 description: str = '',
                 julian_day_format: str = 'days_hours'):
        super().__init__(julian_day_format, reference)
        super(JulianDayCodec, self).__init__(name, default, description)

    @property
    def test_description(self) -> str:
        return (
            'As a DateTime field, it can be filtered by giving a reference '
            'Period, datetime. The tested value from the file name will be '
            'filtered out if it is not included or not equal to the reference '
            'Period or datetime respectively. The reference value can be given '
            'as a string or tuple of string following the numpy timestamp '
            'formatting')

    def test(self, reference: Period | np.datetime64,
             tested: np.datetime64) -> bool:
        if isinstance(reference, Period):
            return reference.intersects(tested)
        else:
            return reference == tested

    @property
    def type(self) -> type[np.datetime64]:
        return np.datetime64


class FileNameFieldInteger(FileNameField):
    """Integer value.

    Attributes
    ----------
    name: str
        name of the field
    """

    def decode(self, input_string: str) -> int:
        try:
            output_integer = int(input_string)
        except ValueError as exc:
            # In case the integer conversion failed. This should not happen if
            # the input regex is properly configured (with groups defined with
            # \d)
            raise FileParsingError(
                f"Number '{input_string}' extracted from filename (group "
                f"'{self.name}') could not be converted to a integer."
            ) from exc

        return output_integer

    def encode(self, data: int) -> str:
        return str(data)

    def test(self, reference: list[int] | slice | int, tested: int) -> bool:
        if isinstance(reference, list):
            return tested in reference
        elif isinstance(reference, slice):
            return reference.start <= tested < reference.stop
        else:
            return tested == reference

    @property
    def test_description(self) -> str:
        return (
            'As a Integer field, it can be filtered by using a reference '
            'value. The reference value can either be a list, a slice or an integer'
            '. The tested value from the file name will be filtered out if it is '
            'outside the given list/slice or not equal to the integer value.')

    @property
    def type(self) -> type[int]:
        return int


class FileNameFieldFloat(FileNameField):
    """Float value.

    Attributes
    ----------
    name: str
        name of the field
    """

    def decode(self, input_string: str) -> float:
        try:
            output_float = float(input_string)
        except ValueError as exc:
            # In case the float conversion failed. This should not happen if
            # the input regex is properly configured (with groups defined with
            # \d)
            raise FileParsingError(
                f"Number '{input_string}' extracted from filename (group "
                f"'{self.name}') could not be converted to a float.") from exc

        return output_float

    def encode(self, data: float) -> str:
        return str(data)

    @property
    def test_description(self) -> str:
        return (
            'As a Float field, it can be filtered by using a reference '
            'float value. The tested value found in the file name will be filtered '
            'out if it is not equal to the reference value.')

    @property
    def type(self) -> type[float]:
        return float


class CaseType(Enum):
    upper = auto()
    lower = auto()


class FileNameFieldEnum(FileNameField):
    """Enum field for files selection.

    Attributes
    ----------
    name: str
        name of the field
    enum_cls:
        enum class
    """

    def __init__(self,
                 name: str,
                 enum_cls,
                 case_type: CaseType | None = None,
                 case_type_encoded: CaseType | None = None,
                 default: type[Enum] | None = None,
                 description: str = ''):
        super().__init__(name, default, description)
        self.enum_cls = enum_cls
        if isinstance(case_type, str):
            case_type = CaseType[case_type]
        self.case_type = case_type

        if isinstance(case_type_encoded, str):
            case_type_encoded = CaseType[case_type_encoded]
        self.case_type_encoded = case_type_encoded

    def decode(self, input_string):
        # Handle difference cases
        if self.case_type == CaseType.upper:
            input_string = input_string.upper()
        elif self.case_type == CaseType.lower:
            input_string = input_string.lower()

        try:
            output_enum = self.enum_cls[input_string]
        except KeyError as exc:
            raise FileParsingError(
                f"Enum '{input_string}' extracted from filename (group "
                f"'{self.name}') could not be converted to a {self.enum_cls.__name__} enum."
            ) from exc

        return output_enum

    def encode(self, data: T) -> str:
        if self.case_type_encoded == CaseType.upper:
            return data.name.upper()
        elif self.case_type_encoded == CaseType.lower:
            return data.name.lower()
        else:
            return data.name

    @property
    def test_description(self) -> str:
        return (
            'As an Enum field, it can be filtered using a reference '
            f'{self.enum_cls} or its equivalent string. The tested value found in '
            'the file name will be filtered out if it is not equal to the given '
            f'enum field. Possible values are: {[e.name for e in self.enum_cls]}'
        )

    def test(self, reference, tested) -> bool:
        if hasattr(reference, '__iter__'):
            return tested in reference
        else:
            return tested == reference

    @property
    def type(self) -> type[Enum]:
        return self.enum_cls


class FileNameFieldPeriod(FileNameField):
    """Period value.

    Attributes
    ----------
    name: str
        name of the field
    date_fmt: str
        date format
    separator: str
        dates separator. Default: '-'
    """

    def __init__(self,
                 name: str,
                 date_fmt: str,
                 separator='_',
                 default: Period | None = None,
                 description: str = ''):
        super().__init__(name, default, description)
        self.date_fmt = date_fmt
        self.separator = separator

    def decode(self, input_string: str) -> Period:
        # If the separator is present in the date format
        if self.separator in self.date_fmt:
            # Find the middle separator and split to get the begin/end dates
            positions = [
                match.start()
                for match in re.finditer(self.separator, input_string)
            ]
            po = positions[len(positions) // 2]
            split = [input_string[:po], input_string[po + 1:]]
        else:
            # Split the period in 2 to get the begin/end dates
            split = input_string.split(self.separator)

        if len(split) != 2:
            raise FileParsingError(
                f"Period '{input_string} extracted from filename(group "
                f"'{self.name}') could not be converted to a Period because it"
                f' could not be separated in two begin/end dates using separator'
                f" '{self.separator}")

        try:
            start_date = np.datetime64(
                dt.datetime.strptime(split[0], self.date_fmt))
            end_date = np.datetime64(
                dt.datetime.strptime(split[1], self.date_fmt))
        except ValueError as exc:
            # In case the date conversion failed. This should not happen if
            # the input regex is properly configured (with groups defined with
            # \d)
            raise FileParsingError(
                f"Date '{input_string}' extracted from filename (group "
                f"'{self.name}') could not be converted to a Period because one"
                f' of its dates could not be converted to a datetime') from exc

        return Period(start_date, end_date)

    def encode(self, data: Period) -> str:
        # dt.datetime does not handle nanosecond precision, so we must convert
        # the numpy timestamp before using dt.datetime to encode the date with
        # the given format
        start = data.start.astype('M8[us]').astype(dt.datetime).strftime(
            self.date_fmt)
        stop = data.stop.astype('M8[us]').astype(dt.datetime).strftime(
            self.date_fmt)
        return start + self.separator + stop

    def test(self, reference: Period | np.datetime64, tested: Period) -> bool:
        return tested.intersects(reference)

    @property
    def test_description(self) -> str:
        return (
            'As a Period field, it can be filtered by giving a reference '
            'Period or datetime. The tested value from the file name will be '
            'filtered out if it does not intersect the reference Period or contain '
            ' the reference datetime. The reference value can be given as a string '
            f'or tuple of string following the {self.date_fmt} formatting')

    @property
    def type(self) -> type[Period]:
        return Period


class FieldFormatter(string.Formatter):

    def __init__(self, fields: dict[str, FileNameField]):
        self._fields = fields
        super().__init__()

    def _vformat(self,
                 format_string,
                 args,
                 kwargs,
                 used_args,
                 recursion_depth,
                 auto_arg_index=0):
        # Override of the _vformat method to intercept the object conversion
        # Taken from string.py
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')
        result = []
        for literal_text, field_name, format_spec, conversion in \
                self.parse(format_string):

            # output the literal text
            if literal_text:
                result.append(literal_text)

            # if there's a field, output it
            if field_name is not None:
                # this is some markup, find the object and do
                #  the formatting

                # handle arg indexing when empty field_names are given.
                if field_name == '':
                    if auto_arg_index is False:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    field_name = str(auto_arg_index)
                    auto_arg_index += 1
                elif field_name.isdigit():
                    if auto_arg_index:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    # disable auto arg incrementing, if it gets
                    # used later on, then an exception will be raised
                    auto_arg_index = False

                # given the field_name, find the object it references
                #  and the argument it came from
                obj, arg_used = self.get_field(field_name, args, kwargs)
                used_args.add(arg_used)

                # PATCH here
                if conversion == 'f':
                    obj = self._fields[field_name].encode(obj)
                else:
                    obj = self.convert_field(obj, conversion)

                # expand the format spec, if needed
                format_spec, auto_arg_index = self._vformat(
                    format_spec,
                    args,
                    kwargs,
                    used_args,
                    recursion_depth - 1,
                    auto_arg_index=auto_arg_index)

                # format the object and append to the result
                result.append(self.format_field(obj, format_spec))

        return ''.join(result), auto_arg_index


@dc.dataclass
class FileNameConvention:
    """Parse or generate filenames with a convention definition.

    The convention is expressed as both a regex and a simple string to handle
    both parsing and generation. The generation string can be omitted and set to
    None if the convention is only used to parse files.

    Parameters
    ----------
    regex: re.Pattern
        pattern for filename matching
    fields: List<FileNameField>
        list of fields, each field name must correspond to a group in the regex pattern
    generation_string: str | None
        string that will be formatted with the input objects to generate a
        string. The string can use the formatting language described in
        help('FORMATTING'). In addition, the formatting can be delegated to each
        field.encode methods by specifying the field name `fn` spec. This allows
        handling more complex objects such as Period. For example with an
        FileNameFieldInteger and FileNameFieldPeriod defined:
        '{cycle_number:>03d}_{period!f}' -> '003_20230102_20240201
    """
    regex: re.Pattern
    fields: list[FileNameField]
    generation_string: str | None = None

    def __post_init__(self):
        self._formatter = FieldFormatter({f.name: f for f in self.fields})
        self._check_consistency()

    def match(self, filename: str) -> tp.Any:
        # Match the file name
        match_object = self.regex.search(filename)
        return match_object

    def parse(self, match_object: re.Match) -> tuple:
        return tuple([
            f.decode(match_object.group(f.name))
            if match_object.group(f.name) is not None else f.default
            for f in self.fields
        ])

    def generate(self, **kwargs):
        if self.generation_string is None:
            raise NotImplementedError(
                "The current file name convention is only configured for parsing. Please specify a 'generation_string' to enable file name generation"
            )
        try:
            return self._formatter.format(self.generation_string, **kwargs)
        except KeyError as exc:
            raise ValueError(
                'Missing arguments to generate the file name') from exc

    def _check_consistency(self):
        self._check_consistency_regex()
        if self.generation_string is not None:
            self._check_consistency_generation_string()

    def _check_consistency_generation_string(self):
        field_names_generation_string = set(
            filter(
                lambda x: x is not None,
                map(lambda x: x[1],
                    self._formatter.parse(self.generation_string))))
        fields_names = {f.name for f in self.fields}

        # Check that the pattern has the necessary groups. It will raise an
        # exception if there is a missing group
        missing_fields = fields_names - field_names_generation_string
        if len(missing_fields) > 0:
            raise ValueError(
                f'Generation string {self.generation_string} misses the '
                f"following fields: '{missing_fields}'")

        # Check that the parser defines all of the regex groups. It will raise
        # an exception if there is a missing field definition
        missing_fields = field_names_generation_string - fields_names
        if len(missing_fields) > 0:
            raise ValueError(
                'The following fields are defined in the generation string but '
                f"not in the FileNameField list: '{missing_fields}'")

    def _check_consistency_regex(self):
        regex_groups = set(self.regex.groupindex.keys())
        fields_names = {f.name for f in self.fields}

        # Check that the pattern has the necessary groups. It will raise an
        # exception if there is a missing group
        missing_regex_groups = fields_names - regex_groups
        if len(missing_regex_groups) > 0:
            raise ValueError(
                f"Regex misses '{self.regex.pattern}' the following fields: "
                f"'{missing_regex_groups}'")

        # Check that the parser defines all of the regex groups. It will raise
        # an exception if there is a missing field definition
        missing_fields = regex_groups - fields_names
        if len(missing_fields) > 0:
            raise ValueError(
                f"Missing fields definition in convention: '{missing_fields}'")


class FileParsingError(Exception):
    pass


class FileListingError(Exception):
    pass


class RecordFilter:
    """Utility class for filtering values.

    Attributes
    ----------
    fields: List[FileNameField]
        the fields to filter
    **references:
        the values of fields used for selection
    """

    def __init__(self, fields: list[FileNameField], **references):
        self.fields = fields
        self.references = references

        fields_names = [f.name for f in fields]
        filter_keys = list(references.keys())

        # The FileNameParser will return a record that is ordered the same as
        # its fields. These fields are passed in the same order in this
        # RecordFilter, which is why we can assume that the fields and record
        # are in matching order here
        try:
            self.index_in_record = [
                fields_names.index(key) for key in filter_keys
            ]
        except ValueError as exc:
            unknown_keys = set(filter_keys) - set(fields_names)
            raise FileListingError(
                f"Tried to build filter on file name fields using unknown keys: '{unknown_keys}'"
            ) from exc

        self._sanitize_references()

    def test(self, record):
        """Test if a record is filtered.

        Parameters
        ----------
        record:
            record to filter

        Returns
        -------
        boolean
            true if the record is filtered
        """
        return all(self.fields[index].test(reference, record[index])
                   for reference, index in zip(self.references.values(),
                                               self.index_in_record))

    def _sanitize_references(self):
        for (key, reference), index in zip(self.references.items(),
                                           self.index_in_record):
            field = self.fields[index]
            time_field = (isinstance(field, FileNameFieldDatetime)
                          or isinstance(field, FileNameFieldDateDelta)
                          or isinstance(field, FileNameFieldPeriod)
                          or isinstance(field, FileNameFieldDateJulian)
                          or isinstance(field, FileNameFieldDateJulianDelta))
            if isinstance(reference, tuple) and time_field:
                start = reference[0] if reference[
                    0] is not None else dt.datetime.min
                stop = reference[1] if reference[
                    1] is not None else dt.datetime.max
                self.references[key] = Period(start=np.datetime64(start),
                                              stop=np.datetime64(stop))
            elif isinstance(reference, str) and time_field:
                self.references[key] = np.datetime64(reference)
            elif isinstance(reference, str) and isinstance(
                    field, FileNameFieldEnum):
                self.references[key] = field.enum_cls[reference]
            elif isinstance(
                    reference, collections.abc.Sequence) and isinstance(
                        field, FileNameFieldEnum
                    ) and len(reference) > 0 and isinstance(reference[0], str):
                self.references[key] = tuple(
                    [field.enum_cls[nested] for nested in reference])


class FileNameFilterer:
    """Utility class for filtering filenames.

    Attributes
    ----------
    parser: FileNameConvention
        filename convention allowing to parse the file names
    filenames: List
        a list of file names
    """

    def __init__(
        self,
        parser: FileNameConvention,
        walkable: IWalkable):
        self.convention = parser
        self.walkable = walkable

    def list(self,
             **filters) -> pda.DataFrame:
        """List files in file system.

        Parameters
        ----------
        **filters
            filters for files selection over the fields declared in the file
            name convention. Each field can accept different a difference filter

        Returns
        -------
        pda.DataFrame
            A pandas's dataframe containing all selected filenames + a column
            per field requested
        """
        record_filter = RecordFilter(self.convention.fields, **filters)

        # Build records
        records = (
            # Filter non matching filenames
            filter(
                record_filter.test,
                # Parse the result and append the filename to the record
                map(
                    lambda file_match:
                    (*self.convention.parse(file_match[1]), file_match[0]),
                    # Filter out non matching files
                    filter(
                        lambda file_match: file_match[1] is not None,
                        # Match file names
                        map(
                            lambda file: (file,
                                            self.convention.match(
                                                os.path.basename(file[0]))),
                            # Walk the folder and find the files
                            self.walkable.walk(**filters))))))

        df = pda.DataFrame(records,
                           columns=[f.name for f in self.convention.fields] +
                           ['filename'])

        return df
