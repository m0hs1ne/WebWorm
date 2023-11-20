import webtech


def detect_tech(url):
    wt = webtech.WebTech(options={"random_user_agent": True})
    try:
        report = wt.start_from_url(url)
        return report
    except webtech.utils.ConnectionException:
        print("Connection error")
        return None
