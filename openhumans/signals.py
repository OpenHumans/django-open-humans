"""
member_deauth: Sent when the 'deauth' webhook URL is called by Open Humans,
   containing the following parameters:
     sender: expected to be OpenHumansMember class
     open_humans_member: OpenHumansMember instance
     erasure_requested: Boolean (whether the member requested erasure)
"""
import django.dispatch


member_deauth = django.dispatch.Signal(providing_args=[
    "open_humans_member", "erasure_requested"])
