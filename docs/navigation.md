# Navigation

`follow_with_planner(points, speed)` (the planner option in WebRosie, on by default, or `goto_with_planner`
and `follow_with_planner` in the [client](client.md)) takes the robot through points around walls and
furniture, finding a route from each point to the next. rosie finds the route in three
steps: grow the obstacles by the robot's size, build a *visibility graph*, and search it with A*. Then the
robot follows the route's corners like any other path.

## Maps

`world/maps.py` · `src/rosie/builtin/maps/house.geojson`

A map is a `.geojson` file: a [GeoJSON](https://geojson.org/) `FeatureCollection` in metres, with a `name`
(how rosie lists it), and one feature per room, wall, door and obstacle, told apart by their `kind` property:

```json
{
  "type": "FeatureCollection",
  "name": "Garage",
  "features": [
    {"type": "Feature", "properties": {"kind": "room", "name": "Garage"},
     "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [4, 0], [4, 3], [0, 3], [0, 0]]]}},
    {"type": "Feature", "properties": {"kind": "wall", "room": "Garage"},
     "geometry": {"type": "MultiLineString", "coordinates": [[[1, 0], [4, 0], [4, 3], [0, 3], [0, 0]]]}},
    {"type": "Feature", "properties": {"kind": "door", "room": "Garage"},
     "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 0]]}},
    {"type": "Feature", "properties": {"kind": "obstacle", "name": "Car", "room": "Garage"},
     "geometry": {"type": "Polygon", "coordinates": [[[1.5, 1], [3.5, 1], [3.5, 2], [1.5, 2], [1.5, 1]]]}}
  ]
}
```

| `kind` | Geometry | Is |
|---|---|---|
| `room` | `Polygon` or `MultiPolygon` | a floor. All the rooms together must make one connected floor |
| `wall` | `LineString` or `MultiLineString` | lines the robot can't cross; the gaps between them are the doors |
| `door` | `LineString` or `MultiLineString` | where WebRosie draws a door (the planner only needs the gap in the walls) |
| `obstacle` | `Polygon` or `MultiPolygon` | furniture; a `MultiPolygon` is several pieces |

Only `kind` is required in `properties`; `name` (of a room or an obstacle) and `room` (the one a wall, door or
obstacle belongs to) are labels for you and for WebRosie. A feature of an unknown kind, or with a geometry its
kind doesn't take, stops rosie with a message naming the file.

Any GeoJSON tool can draw or edit a map: [geojson.io](https://geojson.io) in a browser, or QGIS. Their
coordinates are longitude and latitude, but rosie reads them as metres on the floor, so keep them small.

A map from rosie 1 (a `.json` file with `rooms`, each with `borders`, `walls`, `doors` and `items`) converts
with `scripts/convert_map.py`, which needs only Python:

```bash
python scripts/convert_map.py my-house.json my-house.geojson
```

rosie comes with "Gustavo's House"; your own maps go in the `maps/` folder of your
[robot's profile](robots.md#profiles), and win a name over rosie's. `rosie start --map` picks the map at
start, and `POST /map/{name}` switches it while running.

## Free space

`planning/visibility.py` · `visibility_graph`

The robot isn't a point. Instead of checking its whole body against every obstacle, rosie shrinks the problem:
the floor's outline moves inwards and every obstacle grows outwards by a *clearance*, and then the robot can
be treated as a point in what's left, the **free space**. The clearance is `[planning] clearance` (a fifth
by default) of the robot's longest side (body length or width in its profile). In shapely, that's two
`buffer`s with mitred corners (so the shapes keep their corners): the floor buffered by minus the clearance,
minus the union of the obstacles buffered by it. Obstacles closer than twice the clearance merge, and a door
narrower than that closes: the free space can even split in pieces.

## The visibility graph

The shortest way around polygonal obstacles always bends at their corners. So the graph's vertices are the
corners of the free space (its outline and its holes, the grown obstacles), and two vertices are linked when
the straight line between them stays in the free space: running along an obstacle's side is allowed,
crossing it isn't. Each vertex keeps the list of the vertices it sees.

For each route, the robot's position and the target are added as two more vertices, linked to every vertex
they can see, each other included: a target in plain sight is a straight line. The graph itself is built
once per map and reused.

## A*

`planning/search.py` · `astar_path`

A* explores the graph from the start, always expanding the vertex with the smallest *distance so far plus
straight-line distance to the target*. The straight line never overestimates the remaining distance, so the
first time A* reaches the target it has the shortest route through the graph. If the target can't be reached
(inside furniture, outside the floor, in a closed room) the search runs out of vertices and rosie raises
`NoRouteError`; the web API answers 409, and WebRosie shows the message.

The start is wherever the robot is, which may be closer to a wall or furniture than the clearance (a robot
that starts at the origin, in the house's corner, is). Then the route first goes straight to the nearest
point of the free space, and searches from there.

## Driving the route

`planning/path.py` · `plan_path`, `core.py` · `Robot.follow_with_planner`

The route is a list of corners, and the robot follows them with its [trajectory planner](motion-control.md),
at the order's speed on every stretch. The linear planner drives the route as found; the cubic one
rounds its corners, so it can cut a little into the clearance.

## Try it

- Draw a map of your classroom and drive the simulated robot across it.
- Print the graph: `visibility_graph(load_world(path), 0.1)` gives the free space, the vertices and what each
  vertex sees; plot them with matplotlib on top of the map.
- Change the clearance and watch routes appear and disappear through narrow doors.
- Replace A* with Dijkstra (A* with a zero heuristic) and count how many vertices each one explores.
