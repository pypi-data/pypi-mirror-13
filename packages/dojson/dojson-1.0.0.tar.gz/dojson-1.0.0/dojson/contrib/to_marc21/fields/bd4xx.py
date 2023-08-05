# -*- coding: utf-8 -*-
#
# This file is part of DoJSON
# Copyright (C) 2015 CERN.
#
# DoJSON is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""To MARC 21 model definition."""

from dojson import utils

from ..model import to_marc21


@to_marc21.over('400', '^series_statement_added_entry_personal_name$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_series_statement_added_entry_personal_name(self, key, value):
    """Reverse - Series Statement/Added Entry-Personal Name."""
    indicator_map1 = {"Family name": "3", "Forename": "0", "Surname": "1"}
    indicator_map2 = {
        "Main entry not represented by pronoun": "0",
        "Main entry represented by pronoun": "1"}
    return {
        'a': value.get('personal_name'),
        'x': value.get('international_standard_serial_number'),
        'c': utils.reverse_force_list(
            value.get('titles_and_other_words_associated_with_a_name')),
        'b': value.get('numeration'),
        'e': utils.reverse_force_list(
            value.get('relator_term')),
        'd': value.get('dates_associated_with_a_name'),
        'g': value.get('miscellaneous_information'),
        'f': value.get('date_of_a_work'),
        'k': utils.reverse_force_list(
            value.get('form_subheading')),
        'v': value.get('volume_sequential_designation'),
        'l': value.get('language_of_a_work'),
        'n': utils.reverse_force_list(
            value.get('number_of_part_section_of_a_work')),
        'p': utils.reverse_force_list(
            value.get('name_of_part_section_of_a_work')),
        'u': value.get('affiliation'),
        '4': utils.reverse_force_list(
            value.get('relator_code')),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')),
        't': value.get('title_of_a_work'),
        '$ind1': indicator_map1.get(
            value.get('type_of_personal_name_entry_element'),
            '_'),
        '$ind2': indicator_map2.get(
            value.get('pronoun_represents_main_entry'),
            '_'),
    }


@to_marc21.over('410', '^series_statement_added_entry_corporate_name$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_series_statement_added_entry_corporate_name(self, key, value):
    """Reverse - Series Statement/Added Entry-Corporate Name."""
    indicator_map1 = {
        "Inverted name": "0",
        "Jurisdiction name": "1",
        "Name in direct order": "2"}
    indicator_map2 = {
        "Main entry not represented by pronoun": "0",
        "Main entry represented by pronoun": "1"}
    return {
        'a': value.get('corporate_name_or_jurisdiction_name_as_entry_element'),
        'x': value.get('international_standard_serial_number'),
        'c': value.get('location_of_meeting'),
        'b': utils.reverse_force_list(
            value.get('subordinate_unit')),
        'e': utils.reverse_force_list(
            value.get('relator_term')),
        'd': utils.reverse_force_list(
            value.get('date_of_meeting_or_treaty_signing')),
        'g': value.get('miscellaneous_information'),
        'f': value.get('date_of_a_work'),
        'k': utils.reverse_force_list(
            value.get('form_subheading')),
        'v': value.get('volume_sequential_designation'),
        'l': value.get('language_of_a_work'),
        'n': utils.reverse_force_list(
            value.get('number_of_part_section_meeting')),
        'p': utils.reverse_force_list(
            value.get('name_of_part_section_of_a_work')),
        'u': value.get('affiliation'),
        '4': utils.reverse_force_list(
            value.get('relator_code')),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')),
        't': value.get('title_of_a_work'),
        '$ind1': indicator_map1.get(
            value.get('type_of_corporate_name_entry_element'),
            '_'),
        '$ind2': indicator_map2.get(
            value.get('pronoun_represents_main_entry'),
            '_'),
    }


@to_marc21.over('411', '^series_statement_added_entry_meeting_name$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_series_statement_added_entry_meeting_name(self, key, value):
    """Reverse - Series Statement/Added Entry Meeting Name."""
    indicator_map1 = {
        "Inverted name": "0",
        "Jurisdiction name": "1",
        "Name in direct order": "2"}
    indicator_map2 = {
        "Main entry not represented by pronoun": "0",
        "Main entry represented by pronoun": "1"}
    return {
        'a': value.get('meeting_name_or_jurisdiction_name_as_entry_element'),
        'x': value.get('international_standard_serial_number'),
        'c': value.get('location_of_meeting'),
        'e': utils.reverse_force_list(
            value.get('subordinate_unit')
        ),
        'd': value.get('date_of_meeting'),
        'g': value.get('miscellaneous_information'),
        'f': value.get('date_of_a_work'),
        'k': utils.reverse_force_list(
            value.get('form_subheading')
        ),
        'v': value.get('volume_sequential_designation'),
        'l': value.get('language_of_a_work'),
        'n': utils.reverse_force_list(
            value.get('number_of_part_section_meeting')
        ),
        'q': value.get('name_of_meeting_following_jurisdiction_name_entry_element'),
        'p': utils.reverse_force_list(
            value.get('name_of_part_section_of_a_work')
        ),
        'u': value.get('affiliation'),
        '4': utils.reverse_force_list(
            value.get('relator_code')
        ),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        't': value.get('title_of_a_work'),
        '$ind1': indicator_map1.get(value.get('type_of_meeting_name_entry_element'), '_'),
        '$ind2': indicator_map2.get(value.get('pronoun_represents_main_entry'), '_'),
    }


@to_marc21.over('440', '^series_statement_added_entry_title$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_series_statement_added_entry_title(self, key, value):
    """Reverse - Series Statement/Added Entry-Title."""
    indicator_map2 = {
        "No nonfiling characters": "0",
        "Number of nonfiling characters": "8"}
    return {
        'a': value.get('title'),
        'x': value.get('international_standard_serial_number'),
        'p': utils.reverse_force_list(
            value.get('name_of_part_section_of_a_work')
        ),
        'v': value.get('volume_sequential_designation'),
        'n': utils.reverse_force_list(
            value.get('number_of_part_section_of_a_work')
        ),
        '0': utils.reverse_force_list(
            value.get('authority_record_control_number')
        ),
        'w': utils.reverse_force_list(
            value.get('bibliographic_record_control_number')
        ),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '$ind1': '_',
        '$ind2': indicator_map2.get(value.get('nonfiling_characters'), '_'),
    }


@to_marc21.over('490', '^series_statement$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_series_statement(self, key, value):
    """Reverse - Series Statement."""
    indicator_map1 = {"Series not traced": "0", "Series traced": "1"}
    return {
        'a': utils.reverse_force_list(
            value.get('series_statement')
        ),
        'x': utils.reverse_force_list(
            value.get('international_standard_serial_number')
        ),
        '6': value.get('linkage'),
        'l': value.get('library_of_congress_call_number'),
        '3': value.get('materials_specified'),
        'v': utils.reverse_force_list(
            value.get('volume_sequential_designation')
        ),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '$ind1': indicator_map1.get(value.get('series_tracing_policy'), '_'),
        '$ind2': '_',
    }
