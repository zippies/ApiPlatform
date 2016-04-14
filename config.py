# -*- coding: utf-8 -*-
import os

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)),'data.sqlite')
    SECRET_KEY = 'what does the fox say?'
    WTF_CSRF_SECRET_KEY = "whatever"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__),"app/static")
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    log_path = os.path.join(os.path.dirname(__file__),"logs")

    case_template = """
{% for beforecode in beforecodes %}
{{ beforecode }}
{% endfor %}

response = send_request('{{api.name}}',url='{{api.url}}',method='{{api.type}}',data={{data}},headers={{headers}},timeout={{timeout}})

{% for code in codes %}
{{ code }}
{% endfor %}


{% for endcode in endcodes %}
{{ endcode }}
{% endfor %}

    """


    @staticmethod
    def init_app(app):
        pass
