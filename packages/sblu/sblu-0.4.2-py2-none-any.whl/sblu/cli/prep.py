import os
import tempfile
import subprocess
from itertools import combinations
from itertools import chain as _chain
from collections import OrderedDict

import numpy as np

import click
from path import Path

from ..pdb import (parse_pdb, parse_pdb_stream, fix_atom_records, split_segments,
                   SKIP_RESIDUES, RESNAME_FIXES, RECORD_FIXES)
from ..util import which
from .. import PRMS_DIR


DISU_THRESH_MIN = 1.28925530695 ** 2
DISU_THRESH_MAX = 2.82114477374 ** 2


@click.command()
@click.argument("pdb_file", type=click.File(mode='r'))
@click.option("--all-het-to-atom",
              is_flag=True,
              help="Change all HETATM records to ATOM")
@click.option("--no-skips",
              is_flag=True,
              help="Skip the following residues: " + " ".join(SKIP_RESIDUES))
@click.option(
    "--no-record-fixes",
    is_flag=True,
    help="Change the record_type to ATOM for the following residues: " +
    " ".join(RECORD_FIXES))
@click.option("--no-resname-fixes",
              is_flag=True,
              help="Fix the following residue names:\n" + "\n".join([
                  '\t{} -> {}'.format(k, v) for k, v in list(RESNAME_FIXES.items())
              ]))
@click.option("--outfile",
              type=click.File(mode='w'),
              default=click.open_file('-', 'w'))
def clean(pdb_file, all_het_to_atom, no_skips, no_record_fixes,
          no_resname_fixes, outfile):
    records = fix_atom_records(parse_pdb_stream(pdb_file),
                               no_skips=no_skips,
                               all_het_to_atom=all_het_to_atom,
                               no_record_fixes=no_record_fixes,
                               no_resname_fixes=no_resname_fixes)

    for record in records:
        outfile.write(str(record))


def _splitsegs(records, renum, smod="", output_prefix="segment"):
    outputs = OrderedDict()
    for (segment, chain, segid) in split_segments(records):
        out_file = "{}-{}.{:04d}.pdb".format(output_prefix, chain, segid)
        outputs[(chain, segid)] = out_file

        with open(out_file, "w") as ofp:
            for record in segment:
                record.segment = smod + chain + str(segid)
                ofp.write(str(record).strip()+"\n")
            ofp.write("END\n")

    return outputs


@click.command()
@click.argument("pdb_file", type=click.File(mode='r'))
@click.option("--renum", is_flag=True, help="Renumber residues")
@click.option("--segid/--no-segid", default=True)
@click.option("--output-prefix",
              default=None,
              help="Use this prefix for the output files.")
def splitsegs(pdb_file, renum, segid, output_prefix):
    records = parse_pdb_stream(pdb_file)

    if output_prefix is None:
        if pdb_file.name != "<stdin>":
            output_prefix = os.path.splitext(pdb_file.name)[0]
        else:
            output_prefix = "split_pdb"

    return _splitsegs(records, renum, segid, output_prefix)


@click.command()
@click.argument("segments", nargs=-1)
@click.option("--link")
@click.option("--first")
@click.option("--last")
@click.option("--smod", default="")
@click.option("--wdir")
@click.option("--psfgen", default="psfgen")
@click.option("--nmin", default="nmin")
@click.option("--prm")
@click.option("--rtf")
@click.option("--nsteps", default=1000, type=click.INT)
@click.option("--auto-disu/--no-auto-disu", default=True)
@click.option("--xplor-psf/--no-xplor-psf", default=False)
@click.option("--osuffix")
def psfgen(segments, psfgen, nmin):
    """Generate a PSF file from pdb files"""
    pass


@click.command()
@click.argument("pdb_file", type=click.File(mode='r'))
@click.argument("psf_file", type=click.File(mode='r'))
def nmin(pdb_file, psf_file):
    pass


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--psfgen", default="psfgen")
@click.option("--prefix")
@click.option("--rtf")
def pdb_psf_concat(files, psfgen, prefix, rtf):
    def construct_prefix(psf_files):
        prefix = ""
        for f in files:
            prefix += f.namebase
        return prefix

    def psf_concat(psf_files, rtf_file, prefix, psfgen="psfgen"):
        p = subprocess.Popen([psfgen],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        commands = ""
        commands += "topology {}\n".format(rtf_file)

        for psf_file in psf_files:
            commands += "readpsf {}\n".format(psf_file)

        commands += "writepsf charmm {0}.psf\n".format(prefix)

        p.communicate(commands.encode())

    def pdb_concat(pdb_files, prefix):
        atomi = 0
        with open("{}.pdb".format(prefix), "w") as out_file:
            for pdb in pdb_files:
                last_res_id = ""
                with open(pdb) as in_file:
                    for line in in_file:
                        if line.startswith("ATOM  "):
                            atomi += 1
                            res_id = line[22:27]
                            if atomi >= 99900 and last_res_id != res_id:
                                atomi = 1

                            last_res_id = res_id
                            line = "{0}{1:5d}{2}".format(line[0:6],
                                                         atomi, line[11:])
                        elif line.startswith("HEADER"):
                            atomi = 0
                        if not line.startswith("END"):
                            out_file.write(line)

    if len(files) < 4 or len(files) % 2 != 0:
        raise click.ClickException("Requires at least two pairs of files")

    psf_files = files[::2]
    pdb_files = files[1::2]

    if rtf is None:
        rtf = PRMS_DIR / "pdbamino.rtf"

    if prefix is None:
        prefix = construct_prefix(psf_files)

    psf_concat(psf_files, rtf, prefix, psfgen)
    pdb_concat(pdb_files, prefix)


@click.command()
@click.option("--clean/--no-clean", "clean_pdb", default=True)
@click.option("--minimize/--no-minimize", default=True)
@click.option("--xplor-psf/--no-xplor-psf", default=False)
@click.option("--smod", default="")
@click.option("--out-prefix")
@click.option("--prm", type=click.Path(exists=True))
@click.option("--rtf", type=click.Path(exists=True))
@click.option("chains", "--chain", multiple=True)
@click.option("--psfgen", default="psfgen")
@click.option("--nmin", default="nmin")
@click.option("--nsteps", default=1000, type=click.INT)
@click.option("--auto-disu/--no-auto-disu", default=True)
@click.argument("pdb_file", type=click.File(mode='r'))
def prep(pdb_file, chains, smod, clean_pdb, minimize, prm, rtf, xplor_psf,
         out_prefix, psfgen, nmin, nsteps, auto_disu):
    def is_cys_sulfur(r):
        return r.name == ' SG ' and r.resname == 'CYS'

    workdir = Path(tempfile.mkdtemp())
    if not workdir:
        return

    if not out_prefix:
        out_prefix = "prepared"

    out_prefix = os.path.join(os.path.abspath("."), out_prefix)

    try:
        psfgen = which(psfgen)
        if psfgen is None:
            # TODO: log error
            return

        if clean_pdb:
            records = list(fix_atom_records(parse_pdb_stream(pdb_file,
                                                             only_atoms=True)))
        else:
            records = list(parse_pdb_stream(pdb_file,
                                            only_atoms=True))

        all_segments = _splitsegs(records,
                                  False, smod, workdir/"segment")
        is_wildcard = len(chains) == 0 or '?' in chains
        segments = OrderedDict(
            item for item in list(all_segments.items()) if
            (item[0][0] in chains or  # chain is explicitly named
             (is_wildcard and item[0][0][0] != 'h'))  # wildcard and not het
        )
        records = list(r for segment in list(segments.values()) for r in parse_pdb(segment))

        p = subprocess.Popen([psfgen],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        commands = []
        commands.append("psfcontext mixedcase")
        commands.append("topology {0}".format(rtf))
        coord_commands = []

        for (chain, segid), segment in sorted(segments.items()):
            segid = smod+chain+str(segid)

            seg_cmd = "segment {0} {{ first NONE; last NONE; pdb {1} }}".format(
                segid, segment)
            coord_cmd = "coordpdb {0} {1}".format(segment, segid)
            commands.append(seg_cmd)
            coord_commands.append(coord_cmd)

        # Patch noncontinuous chains
        previous_chain = None
        previous_carbon = None
        for (chain, segid), segment in list(segments.items()):
            if previous_chain is not None and previous_chain != chain:
                previous_carbon = None
                previous_chain = chain
                continue

            segment = list(parse_pdb(segment))

            if previous_carbon:
                nitrogen = None
                for record in segment:
                    if record.name == " N  ":
                        nitrogen = record
                        break

                if nitrogen is not None:
                    delta = nitrogen.coords - previous_carbon.coords
                    dist = np.sqrt(np.sum(np.multiply(delta, delta, delta)))
                    if dist < 1.4:
                        link = (previous_carbon.segment.strip(), previous_carbon.resnum,
                                nitrogen.segment.strip(), nitrogen.resnum)

                        if previous_carbon.resname == "GLY":
                            if nitrogen.resname == "GLY":
                                commands.append("patch JOGG {}:{} {}:{}".format(*link))
                            elif nitrogen.resname == "PRO":
                                commands.append("patch JOGP {}:{} {}:{}".format(*link))
                            else:
                                commands.append("patch JOGA {}:{} {}:{}".format(*link))
                        elif nitrogen.resname == "PRO":
                            commands.append("patch JOAP {}:{} {}:{}".format(*link))
                        elif nitrogen.resname == "GLY":
                            commands.append("patch JOAG {}:{} {}:{}".format(*link))
                        else:
                            commands.append("patch JOAA {}:{} {}:{}".format(*link))

            previous_carbon = None
            for record in segment[::-1]:
                if record.name == " C  ":
                    previous_carbon = record
                    break
            previous_chain = chain

        disulfides = []
        if auto_disu:
            for ri, rj in combinations(list(filter(is_cys_sulfur, records)), 2):
                delta = (ri.coords - rj.coords)
                dist_sq = np.sum(np.multiply(delta, delta, delta))
                if dist_sq > DISU_THRESH_MIN and dist_sq < DISU_THRESH_MAX:
                    disulfides.append((ri.segment.strip(), ri.resnum,
                                       rj.segment.strip(), rj.resnum))

        for link in disulfides:
            commands.append("patch DISU {0}:{1} {2}:{3}".format(*link))

        commands += coord_commands

        commands.append("guesscoord")
        commands.append("writepsf charmm {0}.psf".format(out_prefix))
        if xplor_psf:
            commands.append("writepsf x-plor {0}_xplor.psf".format(out_prefix))
        commands.append("writepdb {0}.pdb".format(out_prefix))

        if not clean_pdb:
            print(("\n".join(commands)))

        stdout, stderr = p.communicate(("\n".join(commands)).encode())

        if minimize and nsteps > 0:
            nmin = which(nmin)
            if nmin is None:
                # TODO: log error
                return

            with open("{0}.pdb".format(out_prefix), "r") as inp, open(workdir/"fixed.pdb", "w") as out:
                for l in inp:
                    if l.startswith("ATOM") and l[55:60] != ' 0.00':
                        out.write(l)

            cmd = [nmin, "{0}.psf".format(out_prefix), prm, rtf,
                   "{0}.pdb".format(out_prefix), workdir/"fixed.pdb", str(nsteps)]
            with open("{0}_nmin.pdb".format(out_prefix), "w") as min_out:
                subprocess.check_call(cmd, stdout=min_out)
    finally:
        if clean_pdb:
            import shutil
            shutil.rmtree(workdir)
        else:
            print(workdir)
