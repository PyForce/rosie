# Navigation

`goto_with_planner(x, y, t)` (or the planner option in WebRosie, or `goto_with_planner` in the
[client](client.md)) takes the robot to a point around walls and furniture. rosie finds the route in three
steps: grow the obstacles by the robot's size, build a *visibility graph*, and search it with A*. Then the
robot follows the route's corners like any other path.

## Maps

`world/maps.py` · `src/rosie/builtin/maps/house.json`

A map is a JSON file of rooms, in metres, with [GeoJSON](https://geojson.org/) shapes:

```json
{
  "name": "Garage",
  "rooms": {
    "Garage": {
      "borders": {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [4, 0], [4, 3], [0, 3]]]}},
      "walls": {"type": "Feature", "geometry": {"type": "MultiLineString", "coordinates": [[[0, 0], [4, 0]]]}},
      "doors": {"type": "Feature", "geometry": {"type": "MultiLineString", "coordinates": []}},
      "items": {
        "Car": {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[1, 1], [3, 1], [3, 2], [1, 2]]]}}
      }
    }
  }
}
```

- **borders**: the room's floor. All the rooms together must make one connected floor.
- **items**: furniture, the obstacles.
- **walls** and **doors**: drawn by WebRosie; the planner uses only the floor and the items.

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

## Driving the route

`planning/path.py` · `plan_path`, `core.py` · `Robot.goto_with_planner`

The route is a list of corners, and the robot follows them with the [trajectory planner](motion-control.md)
of its profile, `t` seconds per straight stretch. The linear planner drives the route as found; the cubic one
rounds its corners, so it can cut a little into the clearance.

## Try it

- Draw a map of your classroom and drive the simulated robot across it.
- Print the graph: `visibility_graph(load_world(path), 0.1)` gives the free space, the vertices and what each
  vertex sees; plot them with matplotlib on top of the map.
- Change the clearance and watch routes appear and disappear through narrow doors.
- Replace A* with Dijkstra (A* with a zero heuristic) and count how many vertices each one explores.
