import argparse
import os

from pathlib import Path


def read_bsdf(filename: Path) -> None:
    """read_bsdf function to read in bsdf files from the Mini-Diff V2"""
    bsdf_file = open(filename, "r")

    # Initial loop to see how many wavebands there are and write out headers in the
    # appropriate files
    wls = []  # Initialise wls as a list
    for aline in bsdf_file:  # Loops through each line
        a = aline.split()  # Split each line with whitespace delimiters
        if not a:  # Skip line if its empty (the if function wont work if it is)
            continue
        elif "Wavelength" in a[0]:
            wls.append(a[1])
    bsdf_file.seek(0)  # Move back to the start of the file

    wls = list(set(wls))  # Form a list of strings
    print("Initialising output files...")
    # Write the header to each output file (also overwrites existing files with the same name)
    for wl in wls:
        outFileName = Path(f"{filename.stem}_{int(wl)}nm.txt")
        if os.path.exists(outFileName):
            continue
        with open(outFileName, "w") as outFile:
            outFile.write("*ThetaI PhiI ThetaR PhiR BRDF\n")

    # Initialise some counters
    f = 0
    azi_count = 0
    rad_count = 0
    for aline in bsdf_file:  # Loops through each line
        f += 1  # Increment counter
        a = aline.split()
        if not a or "#" in a[0]:
            continue
        if any(s in a[0] for s in ["Model", "Source", "Symmetry"]):
            continue
        if (
            "SpectralContent" in a[0]
        ):  # Store a bunch of variables from the header maybe use them in later versions
            SpectralContent = a[1]
        if "ScatterAzimuth" in a[0]:
            ScatterAzimuths = next(bsdf_file).split()
        if "ScatterRadial" in a[0]:
            ScatterRadialAngles = next(bsdf_file).split()
        if "AOI" in a[0]:
            incidence_angle = int(a[1])
        if "POI" in a[0]:
            pois = int(a[1])
        if "Wavelength" in a[0]:
            wavelength = float(a[1])
        if "ScatterType" in a[0]:
            scattertype = a[1]
        if "TIS" in a[0]:
            TIS = a[1]
            print(f"Writing ThetaI={incidence_angle}, {wavelength}nm")
        if "Data" in a[0]:
            continue
        if a[0].replace(".", "").isdigit():
            outFileName = Path(f"{filename.stem}_{wavelength}nm.txt")
            with open(outFileName, "a") as fp:
                for brdf in a:
                    fp.write(
                        f"{incidence_angle} {pois} {int(ScatterRadialAngles[rad_count])} {int(ScatterAzimuths[azi_count])} {float(brdf)}\n"
                    )
                    rad_count += 1
            azi_count += 1
            rad_count = 0
            if azi_count == len(ScatterAzimuths):
                azi_count = 0
    bsdf_file.close()
    print(f"Closing {filename}")

    return


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", default=None, help=".bsdf file to process")
    args = ap.parse_args()

    read_bsdf(Path(args.file))
