from __future__ import division  # python2 compatibility
import dbus


class DBUSSimpleNotify(object):
    proxy = None
    notifyobject = None
    bus = None
    interface = "org.freedesktop.Notifications"
    item = "org.freedesktop.Notifications"
    path = "/org/freedesktop/Notifications"
    valid = True

    @staticmethod
    def setup():
        try:
            if DBUSSimpleNotify.bus is None:
                DBUSSimpleNotify.bus = dbus.SessionBus()
            if DBUSSimpleNotify.proxy is None:
                DBUSSimpleNotify.proxy = DBUSSimpleNotify.bus.get_object(DBUSSimpleNotify.item,
                                                                         DBUSSimpleNotify.path)
            if DBUSSimpleNotify.notifyobject is None:
                DBUSSimpleNotify.notifyobject = dbus.Interface(DBUSSimpleNotify.proxy,
                                                               DBUSSimpleNotify.interface)
        except:
            DBUSSimpleNotify.valid = False

    @staticmethod
    def notify(title, message, timeout=5000):
        if not DBUSSimpleNotify.valid:
            return
        app_name = "Status Messenger"
        id_num_to_replace = 0
        icon = "/usr/share/icons/gnome/32x32/actions/zoom-fit-best.png"
        title = title
        text = message
        actions_list = ''
        hint = ''
        time = timeout  # in ms
        DBUSSimpleNotify.setup()
        DBUSSimpleNotify.notifyobject.Notify(app_name,
                                             id_num_to_replace,
                                             icon,
                                             title,
                                             text,
                                             actions_list,
                                             hint,
                                             time)
