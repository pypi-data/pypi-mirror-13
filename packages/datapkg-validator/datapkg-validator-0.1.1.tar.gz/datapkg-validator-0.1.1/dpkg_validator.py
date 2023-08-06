#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import click
import codecs
import datapackage_validate


@click.command()
@click.argument('datapackage')
def main(datapackage):
    # is it a dir or the json file?
    if os.path.isdir(datapackage):
        json_path = os.path.join(datapackage, "datapackage.json")
    elif os.path.exists(datapackage):
        json_path = datapackage
    json_contents = codecs.open(json_path, 'r', 'utf-8').read()

    try:
        datapackage_validate.validate(json_contents)
        # datapackage_validate.validate(json_contents, schema)
    except datapackage_validate.exceptions.DataPackageValidateException as e:
        click.echo("Errors found in datapackage.json:")
        for err in e.errors:
            # only get the actual error msg
            err_msg = err[0]
            click.echo("  - %s" % err_msg)
