
dig-Stylometry generates the signature for the required fields with the following rules

1) All digits are replaced with D
2) All words starting with capital letter are replaced with C and all lowercase words with w
3) Single letter capital words are replaced with L

On which fields do you want the signature to be computed and name of signature fields ?
You have to specify the jq paths in config file, if field is not present in the specific path - It won't produce any signature
Check the sample config file in tests folder

Arguments:
(a) Input file - required
(b) Output dir - required
(c) Config file - required
(d) file_format - text/sequence (optional) default value is sequence

Sample running of driver program in tests folder:
--------------------------------------------------
python dig-stylometry/digStylometry/tests/testStylometry.py -i dig-stylometry/digStylometry/tests/text-json/input \
-o dig-stylometry/digStylometry/tests/text-json/output/ -c dig-stylometry/digStylometry/tests/config.json \
--file_format text