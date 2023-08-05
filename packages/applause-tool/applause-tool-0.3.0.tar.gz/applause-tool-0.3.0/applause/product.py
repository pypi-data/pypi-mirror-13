from .buaps import ApplauseBuilds
from .utils import get_emails


class ApplauseProduct(object):
    """
    Base class for Applause MBM/SDK API wrappers
    """
    BASE_URL = None
    INSTALLER_STORE_URL = None
    DISTRIBUTE_URL = None

    def __init__(self, session):
        self.session = session
        self.buaps = ApplauseBuilds(session=session)

    def upload_to_buaps(self, app_id, file_path):
        return self.buaps.process_build(file_path, {"app_id": app_id})

    def create_installer(self, token, changelog, set_as_current=False):
        resp = self.session.post(self.INSTALLER_STORE_URL, data={
            "token": token,
            "change_log": changelog,
            "is_current": set_as_current,
        })
        resp.raise_for_status()
        return resp.json()["id"]

    def upload(self, app_id, path, changelog=None, set_as_current=False):
        token = self.upload_to_buaps(app_id, path)
        installer_id = self.create_installer(token, changelog, set_as_current)
        return installer_id

    def distribute(self, company_id, app_id, path, changelog=None, emails=None):
        emails = get_emails(emails)
        installer_id = self.upload(app_id, path, changelog)
        if emails:
            self.session.post(self.DISTRIBUTE_URL.format(company_id=company_id, app_id=app_id), json={
                "installer": installer_id,
                "emails": emails,
            }).raise_for_status()
