"""
Automount utility.
"""

__all__ = ['AutoMounter']


class AutoMounter(object):

    """
    Automount utility.

    Being connected to the udiskie daemon, this component automatically
    mounts newly discovered external devices. Instances are constructed with
    a Mounter object, like so:

    >>> AutoMounter(Mounter(udisks=Daemon()))
    """

    def __init__(self, mounter):
        """
        Store mounter as member variable and connect to the underlying udisks.

        :param Mounter mounter: mounter object
        """
        self._mounter = mounter
        mounter.udisks.connect('device_changed', self.device_changed)
        mounter.udisks.connect('device_added', mounter.auto_add)
        mounter.udisks.connect('media_added', mounter.auto_add)

    def device_changed(self, old_state, new_state):
        """
        Mount newly mountable devices.

        :param Device old_state: before change
        :param Device new_state: after change
        """
        # udisks2 sometimes adds empty devices and later updates them which
        # makes is_external become true not at device_added time:
        if (self._mounter.is_handleable(new_state)
                and not self._mounter.is_handleable(old_state)):
            self._mounter.add(new_state)
