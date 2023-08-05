# -*- encoding: utf-8 -*-
# Copyright (C) 2015  Alejandro López Espinosa (kudrom)

import json
from importlib import import_module

from twisted.python import log

from lupulo.exceptions import NotFoundDescriptor, RequirementViolated
from lupulo.inotify_observer import INotifyObserver


def find_descriptor(klass_name):
    """
        Return the class in the descriptors folder that has as its
        name the argument klass_name
    """
    try:
        module = import_module("lupulo.descriptors.%s" % klass_name)
    except ImportError as e:
        raise NotFoundDescriptor(e.message.split(" ")[-1])
    return getattr(module, klass_name.capitalize())


class DataSchemaManager(INotifyObserver):
    """
        Validates and generates random data for a data schema.
    """
    def __init__(self, fp):
        """
            @param fp is a file handler of the data schema
            @member desc is the dictionary of the data schema
            @events is a set with all of the events defined in the data schema
        """
        super(DataSchemaManager, self).__init__(fp)
        self.fp = fp
        self.compile()

    def compile(self):
        """
            Initializes @member descriptors as a dictionary indexed by
            each event in @events and its value a class loaded with
            find_descriptor
        """
        try:
            self.desc = json.load(self.fp)
        except ValueError as e:
            log.msg(e.message + " in data schema file.")
        else:
            self.events = set(self.desc.keys())

            self.descriptors = {}
            for key, value in self.desc.items():
                klass = find_descriptor(value["type"])
                try:
                    self.descriptors[key] = klass(**value)
                except TypeError:
                    raise RequirementViolated("%s description is wrong" % key)

    def validate(self, data):
        """
            Validates the @param data against the data schema using
            the @member descriptors dictionary.
        """
        try:
            jdata = json.loads(data)
        except ValueError:
            return False

        keys = set(jdata.keys())

        try:
            keys.remove("id")
        except KeyError:
            return False

        if len(keys.difference(self.events)) != 0:
            return False

        for key in keys:
            value = jdata[key]
            desc = self.descriptors[key]
            if not desc.validate(value):
                return False

        return True

    def generate(self, id, descriptors=[]):
        """
            Generates random data for the data schema using the
            @member descriptors dictionary.
        """
        if len(descriptors) == 0:
            descriptors = self.descriptors.keys()

        rt = {}
        for name in descriptors:
            if name in self.descriptors:
                descriptor = self.descriptors[name]
                rt[name] = descriptor.generate()
        rt["id"] = id

        return json.dumps(rt)

    def get_events(self):
        return self.descriptors.keys()

    def inotify_callback(self, jdata):
        """
            Populate jdata with the information that should be forwarded to the
            frontend if something in the data schema changes
        """
        old_descs = set(self.desc.keys())
        self.compile()
        new_descs = set(self.desc.keys())

        added_descs = new_descs.difference(old_descs)
        removed_descs = old_descs.difference(new_descs)

        jdata['added'] = list(added_descs)
        jdata['removed'] = list(removed_descs)
