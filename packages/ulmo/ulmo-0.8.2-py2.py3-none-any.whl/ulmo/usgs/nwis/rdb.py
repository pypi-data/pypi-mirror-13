"""
    ulmo.usgs.rdb
    ~~~~~~~~~~~~~~

    This module provides direct access to `USGS National Water Information
    System`_ Site Service and Parameter codes services which return data 
    in rdb format.


    .. _USGS National Water Information System: http://waterdata.usgs.gov/nwis
"""
import concurrent.futures


def harvest_sites():
    sites = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        sites = executor.map(_get_sites, _states())
            
    sites = {k: v for d in sites for k, v in d.items()}
    df = pd.DataFrame.from_dict(sites, orient='index')
    #for col in ['latitude', 'longitude', 'srs']:
    #    df[col] = df['location'].apply(lambda x: x[col])

    return df


def _get_sites(state):
    url = 'http://waterservices.usgs.gov/nwis/site/?format=rdb,1.0&stateCd=%s&outputDataTypeCd=iv' % state
    return _parse_rdb(url)

def get_parameters(sites):
    chunks = list(_chunks(df.index.tolist()))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        data = executor.map(_site_info, chunks)
    return pd.concat(data, ignore_index=True)


def _chunks(l, n=100):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def _nwis_iv_features(state):
    return nwis.get_sites(state_code=state, service='iv')


def _nwis_iv_parameters(site):
    return {site: nwis.get_site_data(site, service='iv').keys()}


def _states():
    return [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]


def _parse_rdb(url, index=None):
    df = pd.read_table(url, comment='#')
    if index is not None:
        df.index = df[index]

    df = df.ix[1:] #remove extra header line
    return df


def _pm_codes():
    url = (
        'http://nwis.waterdata.usgs.gov/usa/nwis/pmcodes'
        '?radio_pm_search=param_group&pm_group=All+--+include+all+parameter+groups'
        '&pm_search=&casrn_search=&srsname_search=&format=rdb_file'
        '&show=parameter_group_nm&show=parameter_nm&show=casrn&show=srsname&show=parameter_units'
    )

    return _parse_rdb(url, index='parameter_cd')


def _stat_codes():
    url = 'http://help.waterdata.usgs.gov/code/stat_cd_nm_query?stat_nm_cd=%25&fmt=rdb'
    return _parse_rdb(url, index='stat_CD')


def _site_info(sites):
    base_url = 'http://waterservices.usgs.gov/nwis/site/?format=rdb,1.0&sites=%s&seriesCatalogOutput=true&outputDataTypeCd=iv&hasDataTypeCd=iv'
    url = base_url % ','.join(sites)
    return _parse_rdb(url)