import webtech

def detect_tech(url):
    wt = webtech.WebTech(options={'json': True})
    try:
        report = wt.start_from_url(url)
        return report
    except webtech.utils.ConnectionException:
        print("Connection error")
        return None