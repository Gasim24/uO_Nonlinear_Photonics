#2x2 directional coupler using gds factory 
# the directional coupler takes default arguments passed to it 
# adjustable parameters include input and output lengths of s bends,
#   coupling gap, input and output dy offset, and coupling length
# author: Garen Simpson

import argparse
import gdsfactory as gf

def directional_coupler_2x2(**params):
    """
    Generates a 2×2 directional coupler with S‐bends using bend_s.

    Parameters come in as a dictionary (via **params) so they are
    defined only once (in the command-line parser).
    """
    # Extract all parameters from the dictionary:
    input_bend1_size = params["input_bend1_size"]
    input_bend2_size = params["input_bend2_size"]
    output_bend1_size = params["output_bend1_size"]
    output_bend2_size = params["output_bend2_size"]
    coupling_length   = params["coupling_length"]
    wg_width          = params["wg_width"]
    gap               = params["gap"]
    layer             = params["layer"]
    npoints           = params["npoints"]
    cross_section     = params["cross_section"]

    c = gf.Component("directional_coupler_2x2")

    # x0 is the x-coordinate where the coupling region starts.
    x0 = input_bend1_size[0]

    # Calculate the vertical centers in the coupling region:
    coupler_y = (wg_width + gap) / 2.0

    # ----------------
    # 1) Input S-bends
    # ----------------
    # Top input
    top_input = gf.components.bend_s(
        size=input_bend1_size,
        npoints=npoints,
        cross_section=cross_section,
        allow_min_radius_violation=True,
    )
    top_input_ref = c << top_input
    top_input_ref.mirror_y()  # example: mirror top S-bend
    top_input_ref.move((0, input_bend1_size[1] + coupler_y))

    # Bottom input
    bot_input = gf.components.bend_s(
        size=input_bend2_size,
        npoints=npoints,
        cross_section=cross_section,
        allow_min_radius_violation=True,
    )
    bot_input_ref = c << bot_input
    bot_input_ref.move((0, -input_bend2_size[1] - coupler_y))

    # -------------------
    # 2) Coupling Region
    # -------------------
    top_coupler = gf.components.straight(length=coupling_length, width=wg_width, layer=layer)
    top_coupler_ref = c << top_coupler
    top_coupler_ref.move((x0, coupler_y))

    bot_coupler = gf.components.straight(length=coupling_length, width=wg_width, layer=layer)
    bot_coupler_ref = c << bot_coupler
    bot_coupler_ref.move((x0, -coupler_y))

    # -----------------
    # 3) Output S-bends
    # -----------------
    top_output = gf.components.bend_s(
        size=output_bend1_size,
        npoints=npoints,
        cross_section=cross_section,
        allow_min_radius_violation=True,
    )
    top_output_ref = c << top_output
    top_output_ref.move((x0 + coupling_length, coupler_y))

    bot_output = gf.components.bend_s(
        size=output_bend2_size,
        npoints=npoints,
        cross_section=cross_section,
        allow_min_radius_violation=True,
    )
    bot_output_ref = c << bot_output
    bot_output_ref.mirror_y()  # example: mirror bottom output
    bot_output_ref.move((x0 + coupling_length, -coupler_y))

    # ---------------
    # 4) Ports
    # ---------------
    c.add_port("top_in", port=top_input_ref.ports["o1"])
    c.add_port("bot_in", port=bot_input_ref.ports["o1"])
    c.add_port("top_out", port=top_output_ref.ports["o2"])
    c.add_port("bot_out", port=bot_output_ref.ports["o2"])

    return c


def main():
    parser = argparse.ArgumentParser(
        description="Generate a 2x2 directional coupler with S-bends using gf.components.bend_s."
    )
    parser.add_argument("--input_length1", type=float, default=10.0, help="Bend size length for top input S-bend (um)")
    parser.add_argument("--input_offset1", type=float, default=5.0, help="Bend size input offset for top input top S-bend (um)")
    parser.add_argument("--input_offset2", type=float, default=5.0, help="Bend size input offset for top input bottom S-bend (um)")
    parser.add_argument("--input_length2", type=float, default=10.0, help="Bend size length for bottom input S-bend (um)")
    parser.add_argument("--output_length1", type=float, default=10.0, help="Bend size length for top output S-bend (um)")
    parser.add_argument("--output_length2", type=float, default=10.0, help="Bend size length for bottom output S-bend (um)")
    parser.add_argument("--coupling_length", type=float, default=0.0, help="Length of the coupling region (um)")
    parser.add_argument("--wg_width", type=float, default=0.5, help="Waveguide width (um)")
    parser.add_argument("--gap", type=float, default=0.2, help="Gap between waveguides (um)")
    parser.add_argument("--npoints", type=int, default=200, help="Number of points for bend_s")
    parser.add_argument("--cross_section", type=str, default="strip", help="Cross section for the bends")
    parser.add_argument("--layer", type=int, nargs=2, default=[1, 0], help="Layer tuple, e.g., 1 0")

    args = parser.parse_args()

    # Create a dictionary of parameters, all in one place:
    params = dict(
        input_bend1_size=(args.input_length1, args.input_offset1),
        input_bend2_size=(args.input_length2, args.input_offset2),
        output_bend1_size=(args.output_length1, args.input_offset1),
        output_bend2_size=(args.output_length2, args.input_offset2),
        coupling_length=args.coupling_length,
        wg_width=args.wg_width,
        gap=args.gap,
        npoints=args.npoints,
        cross_section=args.cross_section,
        layer=tuple(args.layer),
    )

    # Pass all parameters at once to the function
    c = directional_coupler_2x2(**params)
    c.show()
    c.write_gds("directional_coupler_2x2.gds")


if __name__ == "__main__":
    main()

