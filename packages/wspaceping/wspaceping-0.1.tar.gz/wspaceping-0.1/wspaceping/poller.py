import re

from anoikis.static.systems import system_id, system_name
from anoikis.map.travel import jumps

from twisted.internet import reactor
from twisted.internet.task import LoopingCall


def is_kspace(system):
    # XXX dont use the name of the system!
    target = system_name(system)
    return not re.search("^J\d{6}", target) and not target == "Thera"


class SiggyPoller:
    def __init__(self, browser, systems, notify_callback):
        self.mapped_systems = set([])

        # Systems that should be looked for in connections, this can be fed
        # from multiple sources
        self.systems_of_interest = set(systems)

        self.systems_of_interest = set(
            system_id(system) for system in self.systems_of_interest
        )
        self.browser = browser
        self.notify_callback = notify_callback

        self.poll = LoopingCall(self.refresh)
        self.poll.start(10)

    def clean(self, systems):
        """Remove all holes that are no longer mapped from the connections and
           possibly handle their state change."""
        appended_systems = systems - self.mapped_systems

        for system in appended_systems:
            # A new system needs to be processed to see if it is a system we'd
            # like to track
            # print system, 'was added'
            reactor.callLater(0, self.process, system)

    def process(self, system):
        # See if this is a direct find if it is we process it immediately and
        # block so the direct list can be used to see if indirects should be
        # processed
        if system in self.systems_of_interest:
            self.found_direct(system)
        else:
            # If the system is a kspace then we can see if there are any
            # indirect ways to get to a target.
            if is_kspace(system):
                reactor.callLater(0, self.find_indirect, system)

    def found_direct(self, system):
        reactor.callLater(0, self.notify_callback, system, 'direct')

    def find_indirect(self, system):
        """Check a kspace system for indirect connections to all targets."""
        for target in self.systems_of_interest:
            distance = jumps(system, target)

            if distance > 10:
                continue

            reactor.callLater(0, self.found_indirect, system, target, distance)

    def found_indirect(self, system, target, distance):
        reactor.callLater(
            0, self.notify_callback, target, 'indirect', distance, system)

    def refresh(self):
        # Get the entire chain from siggy
        siggy_map = self.browser.refresh()["chainMap"]["wormholes"]

        systems = set()
        systems.update(int(x['from_system_id']) for _, x in siggy_map.items())
        systems.update(int(x['to_system_id']) for _, x in siggy_map.items())

        # See if the holes on the map have changed and assume this is a first
        # run if there are no mapped systems at all
        if self.mapped_systems and self.mapped_systems != systems:
            # Determine what systems need to be processed
            self.clean(systems)

        # Update our mapped systems list
        self.mapped_systems = systems
