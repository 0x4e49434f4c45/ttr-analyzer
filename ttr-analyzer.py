TTR_DAT = "ttr.dat"
USE_GRAY = False
COLOR_GRAY = 'gray'
DEBUG = False
DEBUG_PAUSE = False

class Route:
    def __init__(self, city1, city2, colors, length):
        self.city1 = city1
        self.city2 = city2
        self.colors = colors
        self.length = length
        self.used = False

    def __str__(self):
        return f"{self.city1} <=> {self.city2}, colors: {self.colors}, length: {self.length}, used: {self.used}"
    
    def toDirectionalString(self, startCity):
        return f"{startCity} => {self.getDestination(startCity)}, colors: {self.colors}, length: {self.length}, used: {self.used}"

    def getDestination(self, startCity):
        if startCity != self.city1 and startCity != self.city2:
            raise ValueError(f"{startCity} is not a valid starting point for route {self.city1} <=> {self.city2}")
        return self.city1 if startCity != self.city1 else self.city2
    
class RouteTrace:
    def __init__(self, route, startCity, color, previousColor):
        self.route = route
        self.startCity = startCity
        self.color = color
        self.previousColor = previousColor

    def __str__(self):
        return f"route: {self.route.toDirectionalString(self.startCity)}, color: {self.color}, previousColor: {self.previousColor}"
    
with open(TTR_DAT) as ttr_dat_file:
    dat_routes = [l.strip() for l in ttr_dat_file.readlines()]

cities = {}

for line in dat_routes:
    city1, city2, colors, length = line.split(" ")
    route = Route(city1, city2, colors.split(','), int(length))
    if DEBUG:
        print(f"Parsed route: {route}")
    for city in [city1, city2]:
        if city in cities:
            cities[city].append(route)
        else:
            cities[city] = [route]

routeStack = []
longestRoute = None
longestLength = 0
for startCity in list(cities):
    if DEBUG:
        print(f"Start city: {startCity}")
    currentLength = 0
    currentColor = None
    currentCity = startCity
    # Initially, add all routes as we have not chosen a color yet
    tracesToExplore = [RouteTrace(r, currentCity, c, None) for r in cities[startCity] for c in r.colors if USE_GRAY or c != COLOR_GRAY]
    while len(tracesToExplore) > 0:
        currentTrace = tracesToExplore.pop()
        routeStack.append(currentTrace)
        # Mark route as used for all colors (we can't use double routes twice)
        currentTrace.route.used = True
        currentLength = currentLength + currentTrace.route.length
        # If we have chosen a color that isn't gray, set currentColor to restrict future choices
        currentColor = currentTrace.color if currentTrace.color != COLOR_GRAY else currentColor
        currentCity = currentTrace.route.getDestination(currentCity)
        if DEBUG:
            print(f"Current city: {currentCity}, current length: {currentLength}, stack:")
            debugCity = currentCity
            for t in routeStack:
                print(f"\t{t}")

        # See if we have found the longest route so far; if so, save a copy of the trace
        if currentLength > longestLength:
            longestLength = currentLength
            longestRoute = routeStack.copy()
        
        # Now add all eligible ongoing routes
        # A route is eligible if it is unused and:
        #  - it matches the current color, OR
        #  - no color has been selected yet
        # Gray routes are always eligible if unused and gray is enabled.
        currentTrace.nextTraces = [RouteTrace(r, currentCity, c, currentColor) for r in cities[currentCity] for c in r.colors if not r.used and (c == currentColor or (currentColor == None and c != COLOR_GRAY) or (c == COLOR_GRAY and USE_GRAY))]
        tracesToExplore = currentTrace.nextTraces
        # If we have further traces to explore, add them
        if len(currentTrace.nextTraces) > 0:
            if DEBUG:
                print(f"Found {len(currentTrace.nextTraces)} further traces.")
        # If we do not have further traces to explore, we have reached a dead end. Backtrack until we reach the next route to explore.
        else:
            if DEBUG:
                print('No further traces found. Backtracking.')
            numBacktrack = 0
            # Backtrack until we have more traces to explore
            while currentTrace != None and len(tracesToExplore) == 0:
                currentCity = currentTrace.startCity
                currentColor = currentTrace.previousColor
                currentLength = currentLength - currentTrace.route.length
                currentTrace.route.used = False
                routeStack.pop()
                if len(routeStack) == 0:
                    # Ran out of stack. If tracesToExplore is still empty, the outer loop will move on to the next starting city.
                    currentTrace = None
                else:
                    currentTrace = routeStack[-1]
                    tracesToExplore = currentTrace.nextTraces
                numBacktrack = numBacktrack + 1
            if DEBUG:
                print(f"Backtracked {numBacktrack} trace(s) to {currentCity}.")

        if DEBUG:
            print('Traces to explore:')
            for t in tracesToExplore:
                print(f"\t{t}")

        if DEBUG_PAUSE:
            input('Press ENTER to continue...')

print(f"Longest single-color route is {longestRoute[0].startCity} => {longestRoute[-1].route.getDestination(longestRoute[-1].startCity)} in {longestRoute[-1].color} ({longestLength} cars). Trace:")
for t in longestRoute:
    print(f"\t{t}")
