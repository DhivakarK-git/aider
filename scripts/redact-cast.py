#!/usr/bin/env python3
import json
import os
import sys

import pyte
from tqdm import tqdm


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input_cast_file output_cast_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Count total lines for progress bar
    total_lines = sum(1 for _ in open(input_file, "r"))

    with open(input_file, "r") as fin, open(output_file, "w") as fout:
        # Process header
        header = fin.readline().strip()
        fout.write(header + "\n")

        # Parse header for terminal dimensions
        header_data = json.loads(header)
        width = header_data.get("width", 80)
        height = header_data.get("height", 24)
        print(f"Terminal dimensions: {width}x{height}")

        # Initialize terminal emulator but don't use it unless necessary
        screen = pyte.Screen(width, height)
        stream = pyte.Stream(screen)

        # Track if we need to check the terminal (if "Atuin" might be on screen)
        check_terminal = False
        atuin_chars = set("Atuin")

        # Process events line by line
        for line in tqdm(fin, desc="Processing events", total=total_lines - 1):
            if not line.strip():
                continue

            # Fast initial check on raw line before JSON parsing
            raw_line_has_atuin_chars = any(char in line for char in atuin_chars)

            # Only parse JSON if we're checking terminal or need to check
            if check_terminal or raw_line_has_atuin_chars:
                event = json.loads(line)

                # For output events, check for potential "Atuin" content
                if len(event) >= 3 and event[1] == "o":
                    output_text = event[2]

                    # Only start checking terminal if we found Atuin chars
                    if raw_line_has_atuin_chars:
                        check_terminal = True

                    if check_terminal:
                        stream.feed(output_text)

                        # Check if "Atuin" is visible on screen
                        atuin_visible = False
                        for display_line in screen.display:
                            if "Atuin" in "".join(display_line):
                                atuin_visible = True
                                break

                        # Reset flag if Atuin is no longer visible
                        if not atuin_visible:
                            check_terminal = False
                        else:
                            continue  # Skip this event if Atuin is visible

                # Write event to output file for non-skipped events
                fout.write(line)
            else:
                # No need to parse JSON if we're not checking terminal
                fout.write(line)


if __name__ == "__main__":
    main()
