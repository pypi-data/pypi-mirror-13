from entity import Entity


class Report(Entity):
    """
    Represents an attribute object.
    """
    id = None
    url = None
    sent_to = None
    sent_to_lists = None
    sent = None
    sendtime = None
    delivered = None
    total_html_opened = None
    unique_html_opened = None
    html_clicks = None
    unsubscribed = None
    bounced = None
    type = None
    finished = None
    preview_url = None
    bounces_url = None
    unsubscribed_url = None
    links_url = None
    opens_url = None
    mail_id = None
    mail_url = None
    mail_subject = None
    sender_name = None
    sender_email = None
    unique_html_clicks = None
    recievers_who_clicked = None
    recievers_who_clicked_24h = None
    bounced_permanent = None
    bounced_temporary = None
    get_view_online_link = None


