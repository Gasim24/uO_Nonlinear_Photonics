### This file generates a gdsfactory script of a subwavelength grating (SWG) edge coupler
### This work was inspired by the following publications 

###Cheben et al., “Broadband Polarization Independent Nanophotonic Coupler for Silicon Waveguides with Ultra-High Efficiency.”
###Cheben et al., “Recent Advances in Metamaterial Integrated Photonics.”
### Authors: Ozan W. Oner and Garen Simpson
#### 

#The edge coupler has 3 main section with the edge coupler tip section which adiabatically tapers from a defined y_initial to y_final adiabatically using a cosine function
#   the next section is a tapering section made from subwavelength grating sections as well as a linear taper, this section tapers linearly
#   the last section is the output waveguide which is a 500nm wide waveguide 
#   for further explanation for the theory on subwavelength couplers and devices see the mentioned works above


import gdsfactory as gf
import numpy as np

def adiabatic_taper(x, start_val, end_val, L):
    """Smooth cosine taper function."""
    return start_val + (end_val - start_val) * (1 - np.cos(np.pi * x / L)) / 2

def create_tip_section(c, args, xpos):
    """Creates the subwavelength grating tip section with tapering period and duty cycle."""
    # First, compute number of grating elements for the tip based on span_tip.
    num_gratings = 0
    x_temp = xpos
    while x_temp + args.final_period_tip <= args.span_tip:
        current_period = adiabatic_taper(x_temp, args.initial_period_tip, args.final_period_tip, args.tapering_length_tip)
        x_temp += current_period
        num_gratings += 1

    # Now place the grating elements consecutively (starting at xpos).
    for _ in range(num_gratings):
        current_period = adiabatic_taper(xpos, args.initial_period_tip, args.final_period_tip, args.tapering_length_tip)
        current_duty_cycle = adiabatic_taper(xpos, args.initial_duty_cycle_tip, args.final_duty_cycle_tip, args.tapering_length_tip)
        current_width = current_duty_cycle * current_period
        current_y_span = adiabatic_taper(xpos, args.initial_y_span_tip, args.final_y_span_tip, args.tapering_length_tip)

        c.add_polygon(
            [
                (xpos - current_width / 2, current_y_span/2),
                (xpos - current_width / 2, -current_y_span/2),
                (xpos + current_width / 2, -current_y_span/2),
                (xpos + current_width / 2, current_y_span/2),
            ],
            layer=(1, 0)
        )
        xpos += current_period

    return xpos  # Return updated position

def create_taper_section(c, args, xpos):
    """
    Creates the grating taper section with linearly varying period and duty cycle,
    then overlaps a linear taper component within the same region.
    """
    # Save the starting x-position of the taper region.
    x_start = xpos
    num_gratings_taper = int(args.taper_span / ((args.initial_period_taper + args.final_period_taper) / 2))

    # Create the grating taper elements over the taper span.
    for _ in range(num_gratings_taper):
        # Use the relative position within the taper region.
        taper_ratio = (xpos - x_start) / args.taper_span  
        current_period = args.initial_period_taper * (1 - taper_ratio) + args.final_period_taper * taper_ratio
        current_duty_cycle = args.initial_duty_cycle_taper * (1 - taper_ratio) + args.final_duty_cycle_taper * taper_ratio
        current_width = current_duty_cycle * current_period
        current_y_span = args.initial_y_span_taper * (1 - taper_ratio) + args.final_y_span_taper * taper_ratio
        initial_taper_width = args.initial_duty_cycle_taper * args.initial_period_taper

        c.add_polygon(
            [
                (xpos - current_width / 2, current_y_span/2),
                (xpos - current_width / 2, -current_y_span/2),
                (xpos + current_width / 2, -current_y_span/2),
                (xpos + current_width / 2, current_y_span/2),
            ],
            layer=(1, 0)
        )
        xpos += current_period

    # --- Overlap the Linear Taper ---
    # Place the linear taper so that it starts at x_start (overlapping the grating taper region).
    taper = gf.components.taper(
        length=args.taper_span,
        width1=args.initial_width_taper,
        width2=args.final_width_taper,
        layer=(1, 0)
    )
    taper_ref = c.add_ref(taper)
    taper_ref.move((x_start - (initial_taper_width / 2), 0))
    # For a fully overlapped design, the output of the taper is at x_start + taper_span.
    xpos = x_start + args.taper_span - initial_taper_width/2

    return xpos  # Return updated position

def create_output_waveguide(c, args, xpos):
    """Creates the final straight output waveguide and adds ports."""  
    wg = gf.components.rectangle(size=(args.output_WG_length, args.final_width_taper))
    wg_ref = c.add_ref(wg)
    wg_ref.move((xpos, -args.final_width_taper / 2))

    # Add ports for connectivity.
    c.add_port(name="o1", center=(-(args.initial_period_tip*args.initial_duty_cycle_tip)/2, 0), width=args.initial_y_span_tip, orientation=180, layer=(1, 0))
    c.add_port(name="o2", center=(xpos + args.output_WG_length, 0), width=args.final_width_taper, orientation=0, layer=(1, 0))
    c = gf.add_pins.add_pins_siepic_optical(c)


def main(args):
    """Main function to construct the subwavelength edge coupler."""
    c = gf.Component("EC_SWG")
    
    xpos = 0  # Start at the origin.
    xpos = create_tip_section(c, args, xpos)        # Add tip section.
    xpos = create_taper_section(c, args, xpos)        # Add tapered grating section overlapped with linear taper.
    create_output_waveguide(c, args, xpos)            # Add output waveguide.

    c.write_gds("EC_SWG.gds")
    c.show()
    return c

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--min_feature_size', type=float, default=0.04)
    parser.add_argument('--output_WG_length', type=float, default=10)

    # Tip Section
    parser.add_argument('--initial_period_tip', type=float, default=0.4)
    parser.add_argument('--final_period_tip', type=float, default=0.35)
    parser.add_argument('--initial_y_span_tip', type=float, default=0.22)
    parser.add_argument('--final_y_span_tip', type=float, default=0.4)
    parser.add_argument('--initial_duty_cycle_tip', type=float, default=0.8)
    parser.add_argument('--final_duty_cycle_tip', type=float, default=0.46)
    parser.add_argument('--tapering_length_tip', type=float, default=1.55)
    parser.add_argument('--span_tip', type=float, default=40)

    # Taper Section
    parser.add_argument('--initial_period_taper', type=float, default=0.35)
    parser.add_argument('--final_period_taper', type=float, default=0.2)
    parser.add_argument('--initial_y_span_taper', type=float, default=0.36)
    parser.add_argument('--final_y_span_taper', type=float, default=0.5)
    parser.add_argument('--initial_duty_cycle_taper', type=float, default=0.5631)
    parser.add_argument('--final_duty_cycle_taper', type=float, default=0.8)
    parser.add_argument('--taper_span', type=float, default=20)

    # Linear Taper (merged with grating taper)
    parser.add_argument('--initial_width_taper', type=float, default=0.1)
    parser.add_argument('--final_width_taper', type=float, default=0.5)

    args = parser.parse_args()
    main(args)