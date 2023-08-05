import os
import requests

url = 'http://web1.ncaa.org/stats/StatsSrv/rankings'

def csv_dump(dir_path='dump', sport_code='MBB', academic_year='2015', rpt_weeks='141', div='1', stat_seq='-103'):
    """
    Starting point. Dumps an unparsed, messy csv. Most inputs are based on 
    arbitrary NCAA codes that users should not have to know (except for maybe 
    sport_code).
    
    :param dir_path:
        Path to directory to dump CSV files in. Defaults to directory called 'dump'
    :param sport_code:
        NCAA code for desired sport. Defaults to Men's Basketball.
    :param academic_year:
        Four digit academic year. Defaults to 2015.
    :param rpt_weeks:
        NCAA code for end week of returned stats. Defaults to end of 12/9/2015.
    :param div:
        NCAA division. Defaults to 1.
    :param stat_seq:
        NCAA code for specific stats requested. Defaults to all team stats.
    """
    payload = { 'sportCode': sport_code,
                'academicYear': academic_year,
                'rptType': 'CSV',
                'rptWeeks': rpt_weeks,
                'div': div,
                'statSeq': stat_seq,
                'doWhat': 'showrankings'
                }
                
    r = requests.post(url, payload)
    files = csv_cleanup(r.content)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
            
    for key in files:
        with open(dir_path+'/'+key+'.csv', 'w') as f:
            f.write(files[key])

def csv_cleanup(content=None):
    """
    Cleans up the csv output from NCAA stats. Separates different tables into 
    individual strings. 
    
    Returns a dictionary with filenames as keys and csv strings as values.
    
    :param content:
        Original output from NCAA stats
    """
    files = {}
    
    if content is None:
        return files
    
    key = ''
    for line in content.split('\n'):
        if 'Division' in line:
            key = line.replace(' ', '')
            files[key] = ''
        if ',' in line:
            files[key] = files[key] + line + '\n'
    
    return files
    
