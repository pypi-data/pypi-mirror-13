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


@to_marc21.over('250', '^edition_statement$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_edition_statement(self, key, value):
    """Reverse - Edition Statement."""
    return {
        'a': value.get('edition_statement'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '3': value.get('materials_specified'),
        'b': value.get('remainder_of_edition_statement'),
        '6': value.get('linkage'),
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over('254', '^musical_presentation_statement$')
@utils.filter_values
def reverse_musical_presentation_statement(self, key, value):
    """Reverse - Musical Presentation Statement."""
    return {
        'a': value.get('musical_presentation_statement'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '6': value.get('linkage'),
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over('255', '^cartographic_mathematical_data$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_cartographic_mathematical_data(self, key, value):
    """Reverse - Cartographic Mathematical Data."""
    return {
        'a': value.get('statement_of_scale'),
        'c': value.get('statement_of_coordinates'),
        'b': value.get('statement_of_projection'),
        'e': value.get('statement_of_equinox'),
        'd': value.get('statement_of_zone'),
        'g': value.get('exclusion_g_ring_coordinate_pairs'),
        'f': value.get('outer_g_ring_coordinate_pairs'),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over('256', '^computer_file_characteristics$')
@utils.filter_values
def reverse_computer_file_characteristics(self, key, value):
    """Reverse - Computer File Characteristics."""
    return {
        'a': value.get('computer_file_characteristics'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '6': value.get('linkage'),
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over('257', '^country_of_producing_entity$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_country_of_producing_entity(self, key, value):
    """Reverse - Country of Producing Entity."""
    return {
        'a': utils.reverse_force_list(
            value.get('country_of_producing_entity')
        ),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '2': value.get('source'),
        '6': value.get('linkage'),
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over('258', '^philatelic_issue_data$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_philatelic_issue_data(self, key, value):
    """Reverse - Philatelic Issue Data."""
    return {
        'a': value.get('issuing_jurisdiction'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        'b': value.get('denomination'),
        '6': value.get('linkage'),
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over('260', '^publication_distribution_imprint$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_publication_distribution_imprint(self, key, value):
    """Reverse - Publication, Distribution, etc. (Imprint)."""
    indicator_map1 = {
        "Current/latest publisher": "3",
        "Intervening publisher": "2",
        "Not applicable/No information provided/Earliest available publisher": "_"}
    return {
        'a': utils.reverse_force_list(
            value.get('place_of_publication_distribution')),
        'c': utils.reverse_force_list(
            value.get('date_of_publication_distribution')),
        'b': utils.reverse_force_list(
            value.get('name_of_publisher_distributor')),
        'e': utils.reverse_force_list(
            value.get('place_of_manufacture')),
        'g': utils.reverse_force_list(
            value.get('date_of_manufacture')),
        'f': utils.reverse_force_list(
            value.get('manufacturer')),
        '3': value.get('materials_specified'),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')),
        '$ind1': indicator_map1.get(
            value.get('sequence_of_publishing_statements'),
            '_'),
        '$ind2': '_',
    }


@to_marc21.over('261', '^imprint_statement_for_films_pre_aacr_1_revised$')
@utils.filter_values
def reverse_imprint_statement_for_films_pre_aacr_1_revised(self, key, value):
    """Reverse - Imprint Statement for Films (Pre-AACR 1 Revised)."""
    return {
        'a': utils.reverse_force_list(
            value.get('producing_company')
        ),
        'b': utils.reverse_force_list(
            value.get('releasing_company')
        ),
        'e': utils.reverse_force_list(
            value.get('contractual_producer')
        ),
        'd': utils.reverse_force_list(
            value.get('date_of_production_release')
        ),
        'f': utils.reverse_force_list(
            value.get('place_of_production_release')
        ),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over('262', '^imprint_statement_for_sound_recordings_pre_aacr_1$')
@utils.filter_values
def reverse_imprint_statement_for_sound_recordings_pre_aacr_1(
        self,
        key,
        value):
    """Reverse - Imprint Statement for Sound Recordings (Pre-AACR 1)."""
    return {
        'a': value.get('place_of_production_release'),
        'c': value.get('date_of_production_release'),
        'b': value.get('publisher_or_trade_name'),
        'k': value.get('serial_identification'),
        'l': value.get('matrix_and_or_take_number'),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over('263', '^projected_publication_date$')
@utils.filter_values
def reverse_projected_publication_date(self, key, value):
    """Reverse - Projected Publication Date."""
    return {
        'a': value.get('projected_publication_date'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '6': value.get('linkage'),
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over(
    '264',
    '^production_publication_distribution_manufacture_and_copyright_notice$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_production_publication_distribution_manufacture_and_copyright_notice(
        self,
        key,
        value):
    """Reverse - Production, Publication, Distribution, Manufacture, and Copyright Notice."""
    indicator_map1 = {"Current/latest": "3", "Intervening": "2",
                      "Not applicable/No information provided/Earliest": "_"}
    indicator_map2 = {
        "Copyright notice date": "4",
        "Distribution": "2",
        "Manufacture": "3",
        "Production": "0",
        "Publication": "1"}
    return {
        'a': utils.reverse_force_list(
            value.get('place_of_production_publication_distribution_manufacture')
        ),
        'c': utils.reverse_force_list(
            value.get('date_of_production_publication_distribution_manufacture_or_copyright_notice')
        ),
        'b': utils.reverse_force_list(
            value.get('name_of_producer_publisher_distributor_manufacturer')
        ),
        '3': value.get('materials_specified'),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        '$ind1': indicator_map1.get(value.get('sequence_of_statements'), '_'),
        '$ind2': indicator_map2.get(value.get('function_of_entity'), '_'),
    }


@to_marc21.over('270', '^address$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_address(self, key, value):
    """Reverse - Address."""
    indicator_map1 = {
        "No level specified": "_",
        "Primary": "1",
        "Secondary": "2"}
    return {
        'a': utils.reverse_force_list(
            value.get('address')
        ),
        'c': value.get('state_or_province'),
        'b': value.get('city'),
        'e': value.get('postal_code'),
        'd': value.get('country'),
        'g': value.get('attention_name'),
        'f': value.get('terms_preceding_attention_name'),
        'i': value.get('type_of_address'),
        'h': value.get('attention_position'),
        'k': utils.reverse_force_list(
            value.get('telephone_number')
        ),
        'j': utils.reverse_force_list(
            value.get('specialized_telephone_number')
        ),
        'm': utils.reverse_force_list(
            value.get('electronic_mail_address')
        ),
        'l': utils.reverse_force_list(
            value.get('fax_number')
        ),
        'n': utils.reverse_force_list(
            value.get('tdd_or_tty_number')
        ),
        'q': utils.reverse_force_list(
            value.get('title_of_contact_person')
        ),
        'p': utils.reverse_force_list(
            value.get('contact_person')
        ),
        'r': utils.reverse_force_list(
            value.get('hours')
        ),
        '4': utils.reverse_force_list(
            value.get('relator_code')
        ),
        '6': value.get('linkage'),
        '8': utils.reverse_force_list(
            value.get('field_link_and_sequence_number')
        ),
        'z': utils.reverse_force_list(
            value.get('public_note')
        ),
        '$ind1': indicator_map1.get(value.get('level'), '_'),
        '$ind2': '_',
    }
