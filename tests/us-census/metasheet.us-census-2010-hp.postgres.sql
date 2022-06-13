
-- us-census-2010-rl.us-census-2010-hp
-- Generated by metasheet on 2021-10-06T09:25:51
create table if not exists "us-census-2010-hp"(
"SERIALNO" int,
"STATE" varchar(2),
"REGION" varchar(1),
"DIVISION" varchar(1),
"PUMA" varchar(5),
"TOTAREA" int,
"LANDAREA" int,
"SUBSAMPL" int,
"HWEIGHT" int,
"PERSONS" int,
"UNITTYPE" varchar(1),
"HSUBFLG" int,
"VACS" varchar(1),
"VACSA" int,
"TENURE" varchar(1),
"TENUREA" int,
"HHT" varchar(1),
"P60" int,
"P65" int,
"P18" int,
"NPF" int,
"NOCH" int,
"NRCH" int,
"PAOC" varchar(1),
"PARC" varchar(1),
"UPART" varchar(1),
"MULTG" varchar(1),
"PNUM" int,
"PSUB" int,
"PWEIGHT" int,
"RELATE" varchar(2),
"RELATEA" int,
"OC" int,
"RC" int,
"SEX" varchar(1),
"SEXA" int,
"SSPA" int,
"AGE" int,
"AGEA" int,
"QTRBIR" int,
"HISPAN" varchar(2),
"HISPANA" int,
"NUMRACE" int,
"WHITE" int,
"BLACK" int,
"AIAN" int,
"ASIAN" int,
"NHAW" int,
"OPI" int,
"OTHER" int,
"RACESHORT" varchar(2),
"RACEDET" varchar(2),
"RACECHKBX" varchar(3),
"RACEA" int,
"GQTYP" varchar(1),
"GQTYPA" int
)
;

-- CSV IMPORT
-- COPY "us-census-2010-hp" from 'path-to-csv-file' DELIMITER ',' CSV HEADER ENCODING 'LATIN1';

