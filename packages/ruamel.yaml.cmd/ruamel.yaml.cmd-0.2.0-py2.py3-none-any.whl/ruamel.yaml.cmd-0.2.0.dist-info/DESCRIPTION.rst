ruamel.yaml.cmd
===============

This package provides the ``yaml`` commandline utlity for converting to/from
YAML and for manipulating YAML files

Basic usage:
------------

- ``yaml round-trip <file_name>`` for basic roundtrip testing of YAML
  files
- ``yaml json <file_name>`` for conversion of JSON file(s) to a single
  YAML block style document
- ``yaml json --write <file_name>`` to convert JSON files to individual .yaml files.
  This is essential for being able to comparing otherwise unreadable JSON files
  (e.g. single line metadata.yaml files in .whl distributions)
- ``yaml ini <file_name>`` for conversion of an INI/config file (ConfigObj
  comment and nested sections supported) to a YAML block style document.
  This requires ``configobj`` to be installed (``pip install configobj``)
- ``yaml from-csv <file_name>`` for conversion CSV to a YAML
  file to a a table in an HTML file.
- ``yaml htmltable <file_name>`` for conversion of the basic structure in a YAML
  file to a a table in an HTML file. The YAML file::

    title:
    - fruit
    - legume
    local:
    - apple
    - sprouts
    import:
    - orange
    - broccoli

  is converted into the table:

  ====== ====== ========
  title  fruit  legume
  local  apple  sprouts
  import orange broccoli
  ====== ====== ========


See ``yaml --help`` for more information on the availble commands


