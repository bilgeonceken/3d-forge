[Server]
host: ${dbtarget}
port: 5432

[Admin]
user: pgkogis
password: ${pgpass}

[Database]
name: forge
user: tileforge
password: tileforge

[Data]
shapefiles: /var/local/cartoweb/tmp/3dpoc/MNT25Swizerland/,/var/local/cartoweb/tmp/3dpoc/WGS84/64/,/var/local/cartoweb/tmp/3dpoc/WGS84/32/,/var/local/cartoweb/tmp/3dpoc/WGS84/16/,/var/local/cartoweb/tmp/3dpoc/WGS84/8/,/var/local/cartoweb/tmp/3dpoc/WGS84/4/,/var/local/cartoweb/tmp/3dpoc/WGS84/2/,/var/local/cartoweb/tmp/3dpoc/WGS84/1/,/var/local/cartoweb/tmp/3dpoc/WGS84/0.5/
tablenames: mnt25_simplified_100m,break_lines_64m,break_lines_32m,break_lines_16m,break_lines_8m,break_lines_4m,break_lines_2m,break_lines_1m,break_lines_0_5m
modelnames: mnt25,bl_64m,bl_32m,bl_16m,bl_8m,bl_4m,bl_2m,bl_1m,bl_0_5m


[Logging]
config: logging.cfg
logfile: /var/log/tileforge/forge_%(timestamp)s.log
sqlLogfile: /var/log/tileforge/sql_%(timestamp)s.log