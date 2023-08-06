#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Cleaner de csvs a partir de reglas de limpieza.

DataCleaner permite aplicar reglas de limpieza a csvs.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import os
import pandas as pd
from dateutil import tz
import arrow


class DataCleaner(object):
    """Limpia csvs a partir de reglas de limpieza."""

    def __init__(self, input_path):
        self.df = pd.read_csv(input_path)
        self.no_args_rules = ["nombre_propio", "string"]

    def clean_file(self, rules, output_path):
        for rule_item in rules:
            for rule in rule_item:
                rule_method = getattr(self, rule)

                if rule in self.no_args_rules:
                    fields = rule_item[rule]
                    for field in fields:
                        rule_method(field, inplace=True)

                else:
                    for args in rule_item[rule]:
                        rule_method(*args, inplace=True)

        self.save(output_path)

    def save(self, output_path):
        """Guarda el DataFrame en un csv.

        Args:
            output_path (str): Ruta donde guardar un archivo csv.
        """
        self.df.set_index(self.df.columns[0]).to_csv(output_path)

    def nombre_propio(self, field, inplace=False):
        """Regla para todos los nombres propios.

        Capitaliza los nombres de países, ciudades, personas, instituciones y
        similares.

        Args:
            field (str): Campo a limpiar

        Returns:
            pandas.Series: Serie de strings limpios
        """
        decoded_series = self.df[field].str.decode("utf-8")
        capitalized = decoded_series.str.title()
        encoded_series = capitalized.str.encode("utf-8")

        if inplace:
            self.df[field] = encoded_series

        return encoded_series

    def string(self, field, inplace=False):
        """Regla para todos los strings.

        TODO: Este método aún no fue implementado!!!

        Aplica un algoritimo de clustering para normalizar strings que son
        demasiado parecidos, sin pérdida de información.

        Args:
            field (str): Campo a limpiar

        Returns:
            pandas.Series: Serie de strings limpios
        """
        # TODO: ya hay un módulo para conseguir la fingerprint key de un string
        # ahora hay que implementar el clustering usando eso
        pass

    def fecha_completa(self, field, time_format, inplace=False):
        """Regla para fechas completas que están en un sólo campo.

        Args:
            field (str): Campo a limpiar.
            time_format (str): Formato temporal del campo.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        decoded_series = self.df[field].str.decode("utf-8")
        parsed_series = decoded_series.apply(self._parse_datetime,
                                             args=(time_format,))
        if inplace:
            self.df["isodatetime_" + field] = parsed_series

        return parsed_series.str.encode("utf-8")

    @staticmethod
    def _parse_datetime(value, time_format):
        try:
            datetime = arrow.get(
                value, time_format,
                tzinfo=tz.gettz("America/Argentina/Buenos Aires"))
            return datetime.isoformat()
        except:
            return pd.np.NaN

    def fecha_separada(self, fields, new_field_name, inplace=False):
        """Regla para fechas completas que están separadas en varios campos.

        Args:
            field (str): Campo a limpiar
            new_field_name (str): Sufijo para agregar a "isodatetime_".

        Returns:
            pandas.Series: Serie de strings limpios
        """
        field_names = [field[0] for field in fields]
        time_format = " ".join([field[1] for field in fields])

        concat_series = self.df[field_names].apply(
            lambda x: ' '.join(x.map(str)),
            axis=1
        )

        parsed_series = concat_series.apply(self._parse_datetime,
                                            args=(time_format,))

        if inplace:
            self.df["isodatetime_" + field] = parsed_series

        return parsed_series.str.encode("utf-8")

    def string_simple_split(self, field, separators, new_field_names,
                            inplace=False):
        """Regla para separar un campo a partir de separadores simples.

        Args:
            field (str): Campo a limpiar
            separators (list): Strings separadores.
            new_field_names (list): Sufijos de los nuevos campos para los
                valores separados.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        decoded_series = self.df[field].str.decode("utf-8")
        parsed_df = decoded_series.apply(self._split, args=(separators,))
        parsed_df.rename(
            columns={key: field + "_" + value
                     for key, value in enumerate(new_field_names)},
            inplace=True
        )

        if inplace:
            self.df = pd.concat([self.df, parsed_df], axis=1)

        return parsed_df

    @staticmethod
    def _split(value, separators):
        values = []
        for separator in separators:
            if separator in str(value):
                values = value.split(separator)
                break

        return pd.Series([str(value).strip() for value in values
                          if pd.notnull(value)])

    def string_regex_split(self, field, pattern, new_field_names,
                           inplace=False):
        """Regla para separar un campo a partir de una expresión regular.

        TODO: Este método aún no fue implementado!!!

        Args:
            field (str): Campo a limpiar.
            pattern (str): Expresión regular.
            new_field_names (list): Sufijos de los nuevos campos para los
                valores separados.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        pass

    def string_peg_split(self, field, grammar, new_field_names, inplace=False):
        """Regla para separar un campo a partir parsing expression grammars.

        TODO: Este método aún no fue implementado!!!

        Args:
            field (str): Campo a limpiar.
            grammar (str): Reglas para compilar una PEG.
            new_field_names (list): Sufijos de los nuevos campos para los
                valores separados.

        Returns:
            pandas.Series: Serie de strings limpios
        """
        pass


def main():
    pass

if __name__ == '__main__':
    main()
