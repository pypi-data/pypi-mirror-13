#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import izip
import argparse
from argparse import RawTextHelpFormatter
import os
import PIL
from PIL import Image


class Androidicon:
    'Create Android Icons'
    def __init__(self):
        self.description = 'Create Android icons\n'
        self.description += ('androidicon [icon type] [image input] '
                             '[res directory]\n\n')
        self.description += 'Icon type options:\n'
        self.description += 'launcher    -> Launcher icons\n'
        self.description += 'stat_notify -> Status bar icons\n'
        self.description += 'menu        -> Menu icons and Action Bar icons\n'
        self.description += 'dialog      -> Dialog icons\n'
        self.description += 'fab         -> Floating action button icons\n'
        self.description += ('generic     -> Generic icons '
                             '(can specify baseline)\n')
        self.description += ('\nThe recommended image input size is at least '
                             '512x512')
        parser = argparse.ArgumentParser(description=self.description,
                                         formatter_class=RawTextHelpFormatter)
        parser.add_argument("type",
                            choices=["launcher", "stat_notify", "menu",
                                     "dialog", "fab", "generic"],
                            help="Icon type")
        parser.add_argument("image",
                            help="Image input")
        parser.add_argument("directory",
                            help="res/ directory",
                            action="store")
        args = parser.parse_args()
        self.iconType = args.type
        self.img = args.image
        self.im = None
        self.resDir = os.path.join(args.directory, '')
        self.drawableFolders = [self.resDir + 'drawable-ldpi/',
                                self.resDir + 'drawable-mdpi/',
                                self.resDir + 'drawable-hdpi/',
                                self.resDir + 'drawable-xhdpi/',
                                self.resDir + 'drawable-xxhdpi/',
                                self.resDir + 'drawable-xxxhdpi/']
        self.mipmapFolders = [self.resDir + 'mipmap-ldpi/',
                              self.resDir + 'mipmap-mdpi/',
                              self.resDir + 'mipmap-hdpi/',
                              self.resDir + 'mipmap-xhdpi/',
                              self.resDir + 'mipmap-xxhdpi/',
                              self.resDir + 'mipmap-xxxhdpi/']
        self.folders = self.drawableFolders
        self.baselineAsset = 0
        self.iconFileName = ''
        self.createAndroidIcon()

    def createAndroidIcon(self):
        self.verifyImageInputSize()
        self.getIconInfo()
        self.createResDirectories()
        self.createIcons()
        print "Complete!"

    def verifyImageInputSize(self):
        self.im = Image.open(self.img)
        width, height = self.im.size
        if width < 512 or height < 512:
            exit('Image input size should be at least 512x512')
        if width != height:
            exit('Image input should have same width and height')

    def getIconInfo(self):
        if self.iconType == 'launcher':
            self.folders = self.mipmapFolders
            self.baselineAsset = 48
            self.iconFileName = 'ic_launcher.png'
        elif self.iconType == 'stat_notify':
            self.baselineAsset = 24
            self.getFileName('ic_stat_notify')
        elif self.iconType == 'menu':
            self.baselineAsset = 32
            self.getFileName('ic_menu')
        elif self.iconType == 'dialog':
            self.baselineAsset = 32
            self.getFileName('ic_dialog')
        elif self.iconType == 'fab':
            self.baselineAsset = 32
            self.getFileName('ic_fab')
        elif self.iconType == 'generic':
            self.getBaselineAsset()
            self.getFileName('ic')
        else:
            print '\nIcon type not available'
            exit()

    def getFileName(self, prefix):
        iconName = raw_input('Icon name (avoid prefix and file extension): ')
        self.iconFileName = prefix + '_' + iconName + '.png'

    def getBaselineAsset(self):
        while True:
            try:
                self.baselineAsset = int(
                    raw_input('Desired baseline (e.g. 48): ')
                )
                break
            except ValueError:
                print "Oops! That was no valid number. Try again..."

    def createResDirectories(self):
        for folder in self.folders:
            if not os.path.exists(os.path.join(os.getcwd(), folder)):
                os.makedirs(os.path.join(os.getcwd(), folder))

    def createIcons(self):
        sizes = [
            0.75,
            1,
            1.5,
            2,
            3,
            4
        ]
        for size, folder in izip(sizes, self.folders):
            tmpim = self.im.resize((
                int(self.baselineAsset * size),
                int(self.baselineAsset * size)
            ), PIL.Image.ANTIALIAS)
            tmpim.save(folder + self.iconFileName)
