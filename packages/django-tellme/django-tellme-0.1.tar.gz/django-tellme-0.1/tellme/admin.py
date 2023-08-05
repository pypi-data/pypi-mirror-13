import json

from django.contrib import admin
from .models import Feedback


# Display an html table from a dict
# Credit: original author Rogerio Hilbert
def pretty_items(r, d, nametag="<strong>%s: </strong>", itemtag='<li>%s</li>\n',
                 valuetag="%s", blocktag=('<ul>', '</ul>\n')):
    if isinstance(d, dict):
        r.append(blocktag[0])
        for k, v in d.items():
            name = nametag % k
            if isinstance(v, dict) or isinstance(v, list):
                r.append(itemtag % name)
                pretty_items(r, v, nametag, itemtag, valuetag, blocktag)
            else:
                value = valuetag % v
                r.append(itemtag % (name + value))
        r.append(blocktag[1])
    elif isinstance(d, list):
        r.append(blocktag[0])
        for i in d:
            if isinstance(i, dict) or isinstance(i, list):
                r.append(itemtag % " - ")
                pretty_items(r, i, nametag, itemtag, valuetag, blocktag)
            else:
                r.append(itemtag % i)
        r.append(blocktag[1])


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("comment", "url", "screenshot_thumb", "user", "created")
    list_filter = ("created", "user", "url")
    search_fields = ("comment", "user__email", "user__name")
    readonly_fields = ("comment", "url", "user", "browser_html", "screenshot_thumb")
    exclude = ('browser', 'screenshot')
    ordering = ("-created",)

    def screenshot_thumb(self, feedback: Feedback):
        if feedback.screenshot:
            return u'<a href="%s" ><img src="%s" width="100"/></a>' % (feedback.screenshot.url, feedback.screenshot.url)
    screenshot_thumb.allow_tags = True
    screenshot_thumb.short_description = "Screenshot"

    def browser_html(self, feedback: Feedback):
        if feedback.browser:
            r = []
            pretty_items(r, json.loads(feedback.browser))
            return u''.join(r)
    browser_html.allow_tags = True
    browser_html.short_description = "Browser Info"

admin.site.register(Feedback, FeedbackAdmin)



