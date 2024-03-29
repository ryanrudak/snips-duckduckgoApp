#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import requests
import json

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

searchurl = "https://api.duckduckgo.com"
lang = "de"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

#def subscribe_intent_callback(hermes, intentMessage):
#    conf = read_configuration_file(CONFIG_INI)
#    action_wrapper(hermes, intentMessage, conf)

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    hermes.publish_continue_session(intentMessage.session_id, u"Ok,",["ryanrudak:searchDuckDuckGo"])
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    # wenn der Indikator ein entsprechendes Wort enthält
    if len(intentMessage.slots.article_indicator) > 0:
        # Schlagwort, nachdem gesucht werden soll in Variable 'article' speichern
        article = intentMessage.slots.article_indicator.first().value
        # Schlagwort an der Konsole (zu debug-Zwecken) ausgeben
        print("Artikel: "+article)
        
        try:
            # ?format=json&pretty=1&lang=de&q=
            query_url = "{}/?q={}&format=json&pretty=1&lang={}".format(searchurl, article, lang)
            print("Query_URL: "+str(query_url))
            headers = {"Accept-Language": "de"}
            results = requests.get(query_url, headers=headers)
            jsonresponse = results.json()
            print("Ergebns: "+str(jsonresponse["AbstractText"]))
            summary = jsonresponse["AbstractText"]
            hermes.publish_end_session(intentMessage.session_id, summary)
        except:
            print("Leider ist ein Fehler aufgetreten:"+str(sys.exc_info()[0]))
            hermes.publish_end_session(intentMessage.session_id, "Leider ist ein Fehler aufgetreten")
    else:
        hermes.publish_end_session(intentMessage.session_id, "Ein Fehler beim Indikator ist aufgetreten")

if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("ryanrudak:searchDuckDuckGo", subscribe_intent_callback)\
        .start()
