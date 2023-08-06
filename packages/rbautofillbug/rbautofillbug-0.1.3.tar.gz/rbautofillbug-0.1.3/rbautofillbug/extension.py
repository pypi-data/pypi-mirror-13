# rbautofillbug Extension for Review Board.

from __future__ import unicode_literals

import logging
import re
import itertools

from django.conf import settings
from django.conf.urls import patterns, include
from django.db.models.signals import post_init, post_delete, pre_save
from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import SignalHook
from reviewboard.reviews.signals import review_request_publishing
from reviewboard.reviews.models import ReviewRequestDraft, ReviewRequest


class AutoFillBugExtension(Extension):
    metadata = {
        'Name': 'Auto Fill Bugs',
        'Summary': 'Extracts bug IDs from the review request summary to fill '
                   'the "Bugs" field automatically.',
    }
    is_configurable = True
    default_settings = {
        'bug_format': "#(\d+)",
    }

    def initialize(self):
        self.already_parsed_drafts = set()
        SignalHook(self, pre_save, self.on_pre_save)
        SignalHook(self, post_delete, self.on_post_delete)

    def on_pre_save(self, sender, instance, **kwargs):
        if sender is ReviewRequestDraft:
            review_request_draft = instance
            logging.debug("pre save for request draft %s",
                          review_request_draft.id)
            if self.need_to_update_bugs_closed(review_request_draft):
                summary = review_request_draft.summary
                bug_regex = self.settings['bug_format']
                bugs = find_bugs(bug_regex, summary)
                review_request_draft.bugs_closed = ', '.join(bugs)
                review_request = review_request_draft.review_request
                logging.info(
                    "Found bugs %s in summary of review request %s",
                     bugs, review_request.get_display_id())
                self.already_parsed_drafts.add(review_request_draft)
                logging.debug("Marking review request draft %s as parsed",
                              review_request_draft.id)

    def on_post_delete(self, sender, instance, using, **kwargs):
        if sender is ReviewRequestDraft:
            review_request_draft = instance
            logging.debug("Removing review request draft %s from parsed drafts",
                          review_request_draft.id)
            self.already_parsed_drafts.discard(review_request_draft)

    def need_to_update_bugs_closed(self, review_request_draft):
        return (review_request_draft.review_request and
                not review_request_draft.review_request.public and
                review_request_draft not in self.already_parsed_drafts and
                review_request_draft.summary)

def find_bugs(bug_regex, summary):
    bug_regex = re.compile(bug_regex)
    bugs = bug_regex.findall(summary)
    # Flatten list if there are multiple groups to match
    if bug_regex.groups > 1:
        bugs = list(itertools.chain.from_iterable(bugs))
    # Remove empty matches
    return filter(None, bugs)

