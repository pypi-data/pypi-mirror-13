"""
Interfacing with the GradScho Degree Request API
"""
import logging
import json
from restclients.models.grad import GradLeave, GradTerm
from restclients.sws.person import get_person_by_regid
from restclients.grad import get_resource, datetime_from_string


PREFIX = "/services/students/v1/api/leave?id="


logger = logging.getLogger(__name__)


def get_leave_by_regid(regid):
    sws_person = get_person_by_regid(regid)
    if sws_person is None:
        return None
    return get_leave_by_syskey(sws_person.student_system_key)


def get_leave_by_syskey(system_key):
    if system_key is None:
        logger.info("get_leave_by_syskey abort, key is None!")
        return None
    url = "%s%s" % (PREFIX, system_key)
    return _process_json(json.loads(get_resource(url)))


def _process_json(data):
    """
    return a list of GradLeave objects.
    """
    requests = []
    for item in data:
        leave = GradLeave()
        leave.reason = item.get('leaveReason')
        leave.submit_date = datetime_from_string(item.get('submitDate'))
        if item.get('status') is not None and len(item.get('status')) > 0:
            leave.status = item.get('status').lower()

        for quarter in item.get('quarters'):
            term = GradTerm()
            term.quarter = quarter.get('quarter').lower()
            term.year = quarter.get('year')
            leave.terms.append(term)
        requests.append(leave)
    return requests
