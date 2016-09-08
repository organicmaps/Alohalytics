from pyaloha.event import Event, DictEvent


class RouteDictEvent(DictEvent):
    def __init__(self, *args, **kwargs):
        super(RouteDictEvent, self).__init__(*args, **kwargs)

        self.setup_mode()

    def setup_mode(self):
        # vehicle, astar-bidirectional-pedestrian
        self.mode = self.data.get(
            'router', self.data.get('name', None)
        )
        if self.mode == 'astar-bidirectional-pedestrian':
            self.mode = 'pedestrian'

    def process_me(self, processor):
        processor.process_routing(self)


# ALOHA: Routing_CalculatingRoute [
#   distance=51797.4 elapsed=6.56531
#   finalLat=49.45913 finalLon=35.11263
#   name=vehicle result=NoError
#   startDirectionX=0 startDirectionY=0
#   startLat=49.55215 startLon=34.52105
# ]
#
# Event for route creation with specific props:
# mode: {'vehicle', 'pedestrian'}
# start: (lat, lon)
# destination: None or (lat, lon)
# status: {None, 'NoError', 'Cancelled'}
# distance:

class RouteRequest(RouteDictEvent):
    keys = (
        'Routing_CalculatingRoute',
    )

    def __init__(self, *args, **kwargs):
        super(RouteRequest, self).__init__(*args, **kwargs)

        self.start = self.user_info.get_location() or (
            self.data['startLat'], self.data['startLon']
        )

        try:
            self.destination = (
                self.data['finalLat'], self.data['finalLon']
            )
        except KeyError:
            self.destination = None

        try:
            self.status = self.data['result']
        except KeyError:
            self.status = None

        try:
            self.distance = self.data['distance']
        except KeyError:
            self.distance = None


# Event for a start of the route with specific props
# with no specific fields

class RouteStart(Event):
    keys = (
        'Routing. Start',
    )

    def process_me(self, processor):
        processor.process_routing(self)


# ALOHA: RouteTracking_RouteClosing [
#   distance=513244 percent=0.197765
#   rebuildCount=0 router=vehicle
# ] <utc=0,lat=44.4369109,lon=8.9513113,acc=1.00>
#
# ALOHA: RouteTracking_ReachedDestination [
#   passedDistance=3.1224
#   rebuildCount=0 router=vehicle
# ]

class RouteEnd(RouteDictEvent):
    keys = (
        'RouteTracking_RouteClosing',
        'RouteTracking_ReachedDestination'
    )

    def __init__(self, *args, **kwargs):
        super(RouteEnd, self).__init__(*args, **kwargs)

        try:
            self.rebuild_count = int(self.data['rebuildCount'])
        except KeyError:
            self.rebuild_count = None

        self.distance_done = self.data.get(
            'distance', self.data.get('passedDistance', None)
        )

        self.percent = float(self.data.get('percent', 100))


class RouteTracking(Event):
    keys = (
        'RouteTracking_PercentUpdate',
    )

    def __init__(self, *args, **kwargs):
        super(RouteTracking, self).__init__(*args, **kwargs)