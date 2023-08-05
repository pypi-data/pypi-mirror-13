# Copyright (c) 2015-2016 Truveris, Inc. All Rights Reserved.
# See included LICENSE file.

from trac.core import Component
from trac.core import implements
from trac.ticket.api import ITicketChangeListener, TicketSystem

from base import TracMattermostComponent


class TicketNotifications(Component, TracMattermostComponent):

    implements(ITicketChangeListener)

    def format_ticket(self, ticket):
        return (
            u"[#{ticket_id}. {summary}]({link})"
            .format(
                ticket_id=ticket.id,
                link=self.env.abs_href.ticket(ticket.id),
                summary=ticket["summary"],
            )
        )

    def format_changes(self, ticket, old_values):
        field_labels = TicketSystem(self.env).get_ticket_field_labels()

        formatted = []
        for k, v in old_values.items():
            # No changes occurred, this sometimes happens when the user clicks
            # on a field but doesn't change anything.
            if v == ticket[k]:
                continue

            if not v:
                f = u"* **{}** set to _{}_".format(field_labels[k], ticket[k])
            elif not ticket[k]:
                f = u"* **{}** unset".format(field_labels[k])
            else:
                if len(v) > 100 or len(ticket[k]) > 100:
                    f = u"* **{}** changed".format(field_labels[k])
                else:
                    f = (
                        u"* **{}** changed from _{}_ to _{}_"
                        .format(field_labels[k], v, ticket[k])
                    )
            formatted.append(f)

        return u"\n".join(formatted)

    def ticket_created(self, ticket):
        text = (
            u"New ticket: {ticket} by @{username}"
        ).format(
            ticket=self.format_ticket(ticket),
            username=ticket["reporter"],
        )

        self.send_notification(text)

    def ticket_changed(self, ticket, comment, author, old_values):
        if len(comment) > 100:
            comment = comment[:97] + "..."

        if old_values:
            fmt = (
                u"@{username} changed {ticket}:\n"
                "{changes}\n\n"
                "{comment}"
            )
        else:
            fmt = (
                u"@{username} commented on {ticket}:\n"
                "{comment}"
            )

        text = fmt.format(
            ticket=self.format_ticket(ticket),
            username=author,
            comment=comment,
            changes=self.format_changes(ticket, old_values),
        ).strip()

        self.send_notification(text)
