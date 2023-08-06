import glob
import os
import click
import pkg_resources
import struct
import tempfile
import shutil
import uuid
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
import warnings

try:
    import zlib
    compression = ZIP_DEFLATED
except:
    warnings.warn('Unable to load zlib, unable to compress files into LPK (stored instead)')
    compression = ZIP_STORED


GEOM_TYPES = {
    1: 'point',
    3: 'line',
    5: 'polygon',
    8: 'point',  # MultiPoint
    11: 'point',  # PointZ
    13: 'line',  # PolylineZ
    15: 'polygon'  # PolygonZ
}
# other types not yet supported

LYR = '0000data.lyr'

PKINFO = """<?xml version="1.0" encoding="utf-8" ?>
<?xml-stylesheet type="text/xsl" href="http://www.arcgisonline.com/home/pkinfostylesheet.xsl"?>
<pkinfo Culture='en-US'>
<ID>{0}</ID>
<name>Data</name>
<version>10.3</version>
<size>-1</size>
<created></created>
<type>Layer Package</type>
<servable>false</servable>
<packagelocation></packagelocation>
<pkinfolocation></pkinfolocation>
</pkinfo>"""
# Note: UUID needs to be updated in pkinfo


def create_lpk(shpfilename, outfilename):

    # open shapefile in binary mode
    # seek to byte 32: https://www.esri.com/library/whitepapers/pdfs/shapefile.pdf page 4
    geom_type_code = None
    with open(shpfilename, 'rb') as f:
        f.seek(32)
        geom_type_code = struct.unpack('i', f.read(4))[0]

    if not geom_type_code in GEOM_TYPES:
        raise ValueError('Geometry type of shapefile not supported: {0}'.format(geom_type_code))

    geom_type = GEOM_TYPES[geom_type_code]


    tmpdir = tempfile.mkdtemp()

    try:
        lyr_dir = os.path.join(tmpdir, 'v10')
        os.mkdir(lyr_dir)
        shutil.copy(
            os.path.join(pkg_resources.resource_filename(__name__, 'lyr/{0}.lyr'.format(geom_type))),
            os.path.join(lyr_dir, LYR)
        )

        esri_dir = os.path.join(tmpdir, 'esriinfo')
        os.mkdir(esri_dir)
        with open(os.path.join(esri_dir, 'item.pkinfo'), 'w') as outfile:
            outfile.write(PKINFO.format(str(uuid.uuid4())))

        shp_dir = os.path.join(tmpdir, 'commondata', 'data')
        os.makedirs(shp_dir)
        in_shp_dir, shp = os.path.split(shpfilename)
        shp_root = os.path.splitext(shp)[0]
        for filename in glob.glob(os.path.join(in_shp_dir, shp_root + '.*')):
            if not filename.endswith('.lock'):
                shutil.copy(filename, os.path.join(shp_dir, os.path.split(filename)[1].replace(shp_root, 'data')))

        with ZipFile(outfilename, 'w', compression=compression) as zf:
            for root, dirs, filenames in os.walk(tmpdir):
                for filename in filenames:
                    zf.write(os.path.join(root, filename), os.path.join(os.path.relpath(root, tmpdir), filename))

    finally:
        shutil.rmtree(tmpdir)



@click.command(short_help="Create a simple ArcGIS layer package from a shapefile")
@click.argument('shp')
def pkg_lpk(shp):
    """Example:

    \b
    > pkg_lpk in.shp
    creates file in.lpk

    wildcards allowed:
    \b
    > pkg_lpk *.shp
    """

    for shp in glob.glob(shp):
        create_lpk(shp, shp.replace('.shp', '.lpk'))


