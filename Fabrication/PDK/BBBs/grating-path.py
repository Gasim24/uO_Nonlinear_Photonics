import gdsfactory as gf
from gdsfactory.cross_section import ComponentAlongPath

# Create the path
# p = gf.path.straight()
# p += gf.path.arc(10)
# p += gf.path.straight()

P = gf.Path()


# Create the basic Path components
left_turn = gf.path.euler(radius=5, angle=90)
right_turn = gf.path.euler(radius=5, angle=-90)
straight_120 = gf.path.straight(length=120)
straight_110 = gf.path.straight(length=110)


# Assemble a complex path by making list of Paths and passing it to `append()`
P.append(
    [
        straight_110,
        right_turn,
        right_turn,
        straight_120,
        left_turn,
        left_turn,
        straight_120,
        right_turn,
        right_turn,
        straight_120,
        left_turn,
        left_turn,
        straight_120,
        right_turn,
        right_turn,
        straight_110,


    ]
)

# f = P.plot()

# Define a cross-section with a via
grating = ComponentAlongPath(
    component=gf.c.rectangle(size=(0.315, 1), centered=True), spacing=0.515, padding=1
)


s = gf.Section(width=0.01, offset=0, layer=(2, 0), port_names=("o1", "o2"))
x = gf.CrossSection(sections=[s], components_along_path=[grating])

# Combine the path with the cross-section
c = gf.path.extrude(P, cross_section=x)
c.show()


