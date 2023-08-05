# -*- coding:utf-8 -*-
import logging
import os.path
import subprocess
logger = logging.getLogger(__name__)


class TemplateInstaller(object):
    def __init__(self, config):
        self.config = config

    def install(self, data, upgrade=False, tag=None):
        logger.info("install {data[name]}".format(data=data))
        outdir = os.path.join(self.config.store_dir, data["name"].replace("/", "."))
        if tag is not None:
            outdir = "{}@{}".format(outdir, tag)

        if not os.path.exists(outdir):
            if tag:
                subprocess.call(["git", "clone", "--depth=1", "-b", tag, data["url"], outdir])
            else:
                subprocess.call(["git", "clone", "--depth=1", data["url"], outdir])
        elif upgrade:
            subprocess.call("""
            cd {path};
            git pull
            """.format(path=outdir), shell=True)
        else:
            print("already installed. ({path})".format(path=outdir))
