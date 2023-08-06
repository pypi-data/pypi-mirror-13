#!/usr/bin/python
#-*- coding: UTF-8 -*-

import os
import re
import subprocess


class AffRender(object):
    def __init__(
            self,
            pdb_list=None,
            output=None,
            nums=list(),
            draw_nums=False,
            guess_nums=False,
            lowt=10,
            width=640, height=480,
            moltype="general",
            clear=False,
            *args, **kwargs):

        self.models = pdb_list

        if output is None:
            self.out = 'out.png'
        else:
            self.out = output

        self.nums = nums
        self.draw_nums = draw_nums
        self.guess_nums = guess_nums

        if self.draw_nums and not self.guess_nums:
            if len(self.nums) != len(self.models):
                raise(Exception("Numbers of models and nums are different"))

        self.width = width
        self.height = height

        self.moltype = moltype

        self.clear = clear

        self.pymol = self.init_pymol()
        self.process_models()

    @staticmethod
    def init_pymol():
        import __main__
        __main__.pymol_argv = ['pymol', '-qc']
        import pymol
        pymol.finish_launching()
        return pymol

    def setup_scene(self):

        self.pymol.cmd.set("ambient", '0.00000')
        self.pymol.cmd.set("antialias", 4)
        self.pymol.cmd.set("light_count", 1)
        self.pymol.cmd.set("ray_opaque_background", 1)
        self.pymol.cmd.set("ray_shadow", 'off')
        self.pymol.cmd.set("reflect_power", '0.10000')
        self.pymol.cmd.set("spec_power", '0.00000')
        self.pymol.cmd.set("specular", '0.00000')

        self.pymol.cmd.bg_color("white")

    @staticmethod
    def tile(images, out, direction="h"):

        tile_format_d = {
            'h': "%dx",
            'v': "x%d"}

        tile_format = tile_format_d[direction] % len(images)

        call = [
            'montage',
            '-mode', 'Concatenate',
            '-tile', tile_format]
        call.extend(images)
        call.append(out)

        subprocess.call(call)

    ### DNA origami specific part ###

    @staticmethod
    def is_backbone(i, j):
        return True if abs(i - j) == 1 else False

    @staticmethod
    def is_crossover(i, j):
        return True if abs(i - j) > 1 else False

    def draw_backbone(self):
        # Get total number of atoms
    #    N = self.pymol.cmd.count_atoms()

        # Show backbone with sticks
    #    for i in range(1, N):
    #        self.pymol.cmd.select('bck', 'resi %d+%d' % (i, i + 1))
    #        self.pymol.cmd.show('sticks', 'bck')

        # Set sticks width
        self.pymol.cmd.show("sticks")
        self.pymol.cmd.set("stick_radius", 1.5)

        # Find single stranded regions
        space = {"single": []}
        self.pymol.cmd.iterate("resn S*", "single.append(resi)", space=space)
        single = map(int, space["single"])

        # Set stich width for single stranded region
        # Only change stick radius for contigious regions in backbone
        # and do not touch crossovers
        if len(single) >= 2:
            for s in range(len(single) - 1):
                i = single[s]
                j = single[s + 1]
                if self.is_backbone(i, j):
                    self.pymol.cmd.set_bond(
                        "stick_radius", 0.5,
                        "i. %d" % i, "i. %d" % j)

        # Color bacbone according to B-factors
        self.pymol.cmd.spectrum("b")

    def draw_crossovers(self, fname):
        """ Read all CONECT from model file and draw all non-backbone
        bonds with dashes"""

        def get_ind(line):
            line = line.strip()
            line = re.sub('\s+', ';', line)
            i, j = map(int, line.split(";")[1:3])
            return i, j

        def is_bond(line):
            return True if re.match('CONECT', line) else False

        with open(fname, 'r') as f:
            bonds = f.readlines()

        crossover = []
        backbone = []

        for b in bonds:
            if is_bond(b):
                i, j = get_ind(b)
                if self.is_crossover(i, j):
                    crossover.append((i, j))
                elif self.is_backbone(i, j):
                    backbone.append((i, j))

        for b in crossover:
            i, j = b
            self.pymol.cmd.unbond("i. %d" % i, "i. %d" % j)
            self.pymol.cmd.distance("i. %d" % i, "i. %d" % j)
        self.pymol.cmd.hide("labels")

        self.pymol.cmd.set("dash_color", "gray80")
        self.pymol.cmd.set("dash_gap", 0)
        self.pymol.cmd.set("dash_length", 4)
        self.pymol.cmd.set("dash_radius", 1.0)

    def draw_nucleic_acid(self):
        self.pymol.cmd.hide("everything")
        self.pymol.cmd.show("lines")
        #self.pymol.cmd.show("cartoon")
        #self.pymol.cmd.set("cartoon_nucleic_acid_mode", 1)
        #self.pymol.cmd.set("cartoon_tube_radius", 0.1)
        #self.pymol.cmd.set("cartoon_ring_finder", 2)
        #self.pymol.cmd.set("cartoon_ring_mode", 2)
        #self.pymol.cmd.set("cartoon_flat_sheets", 0)

        # Color bacbone according to B-factors
        self.pymol.cmd.spectrum("b")

    @classmethod
    def gen_label(self, basename="gg", num=100, width=640, height=480):

        lwidth = int(0.2 * width)  # 20% - empirically
        border = int(0.05 * lwidth)  # Border is 5% of label width

        name = self.gen_name(basename, 0)

        call = [
            "convert",
            "-background", "white",
            "-bordercolor", "white",
            "-size",
            "%dx%d" % (lwidth - 2 * border, height - 2 * border),
            "-border", "%d" % border,
            "-gravity", "East",
            "-pointsize", "%d" % int(lwidth / 3),
            "caption:%d%%" % num,
            name]

        subprocess.call(call)

        return name

    def ray(self, name, width=640, height=480):
        #ray 3200, 2400
        #pymol.cmd.png("DDD.png", dpi=1000)
        #pymol.cmd.ray("3200", "2400")
        #pymol.cmd.zoom("all", 100)
        self.pymol.cmd.zoom("all")
        self.pymol.cmd.ray(width, height)
        self.pymol.cmd.save(name)

    @staticmethod
    def gen_name(basename, number):
        return basename + '_' + str(number) + '_' + '.png'

    def ray_poses(self, basename="gg", width=640, height=480):

        images = []

        name = self.gen_name(basename, 1)
        self.pymol.cmd.orient()
        self.ray(name, width, height)
        images.append(name)

        name = self.gen_name(basename, 2)
        self.pymol.cmd.rotate("x", 90)
        self.ray(name, width, height)
        images.append(name)

        name = self.gen_name(basename, 3)
        self.pymol.cmd.rotate("y", 90)
        self.ray(name, width, height)
        images.append(name)

        return images

    def process_model(self, index):

        model = self.models[index]

        #basename = model.replace('.pdb', '.png')
        basename = model[:-4] + '_tmp'

        self.pymol.cmd.reinitialize()
        # Desired pymol commands here to produce and save figures
        self.setup_scene()

        self.pymol.cmd.load(model)

        if self.moltype == "general":
            self.draw_nucleic_acid()
        elif self.moltype == "origami":
            self.draw_crossovers(model)
            self.draw_backbone()

        images = list()

        if self.draw_nums:
            if self.guess_nums:
                num = self.get_num(model)
            else:
                num = self.nums[index]

            label = self.gen_label(
                basename, num, width=self.width, height=self.height)
            images.append(label)

        poses = self.ray_poses(basename, width=self.width, height=self.height)

        images.extend(poses)

        name = basename + '.png'
        self.tile(images=images, out=name)

        if self.clear:
            map(os.remove, images)

        return name

    @staticmethod
    def get_num(model):
        """ Get representativeness of current model """
        try:
            # try to parse filename like frameXXXX_aff_YY.pdb
            num = re.search('aff_(\d+)', model).groups()[0]
        except:
            # if no, set default num
            raise(Exception("Unable to get num from filename"))
        return int(num)

    def process_models(self):

        images = list()

        for i in range(len(self.models)):

            # now you can call it directly with basename
            image = self.process_model(i)
            images.append(image)

        self.tile(images, self.out, direction='v')

        if self.clear:
            map(os.remove, images)

if __name__ == "__main__":

    import argparse as ag

    def get_args():
        """Parse cli arguments"""
        parser = ag.ArgumentParser(
            description='Render affitiny propagation results')

        parser.add_argument('-f', '--files',
                            nargs='+',
                            dest='pdb_list',
                            required=True,
                            help='PDB file')

        parser.add_argument('-o', '--output',
                            required=True,
                            metavar='output.png',
                            help='Output PNG image')

        parser.add_argument('--nums',
                            nargs='*', type=int,
                            help='Values for numerical labels')

        parser.add_argument('--draw_nums',
                            action='store_true',
                            help='Draw numerical labels')

        parser.add_argument('--guess_nums',
                            action='store_true',
                            help='Guess nums from filenames',
                            default=False)

        parser.add_argument('--clear',
                            action='store_true',
                            help='Clear intermidiate files')

        parser.add_argument('--width',
                            nargs='?', type=int, default=640,
                            help='Width of individual image')

        parser.add_argument('--height',
                            nargs='?', type=int, default=480,
                            help='Height of individual image')

        parser.add_argument('--moltype',
                            nargs='?', type=str, default="general",
                            choices=["general", "origami"],
                            help='Height of individual image')

        args_dict = parser.parse_args()

        return vars(args_dict)

    args = get_args()

    AffRender(**args)
